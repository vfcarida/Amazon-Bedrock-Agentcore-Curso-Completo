"""Setup AgentCore Gateway with Task API target.

Creates an AgentCore Gateway and connects it to the Task Management API
deployed via API Gateway. Supports both NONE and CUSTOM_JWT auth modes.

Run from notebook or command line:
    python setup_gateway.py

Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-gateway.html
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import utils

import boto3
from botocore.exceptions import ClientError


def create_gateway(
    gateway_name: str = "aria-gateway",
    use_jwt: bool = True,
    gateway_role_arn: str | None = None,
    rest_api_id: str | None = None,
    user_pool_id: str | None = None,
    cognito_client_id: str | None = None,
) -> dict:
    """Create an AgentCore Gateway with Task API target. Idempotent.

    Args:
        gateway_name: Name for the gateway.
        use_jwt: Whether to use CUSTOM_JWT auth (requires Cognito).
        gateway_role_arn: IAM role for the gateway. Auto-discovered if None.
        rest_api_id: API Gateway REST API ID. Auto-discovered if None.
        user_pool_id: Cognito User Pool ID. Auto-discovered if None.
        cognito_client_id: Cognito Client ID. Auto-discovered if None.

    Returns:
        Dict with gateway_id, gateway_url, gateway_arn.
    """
    region = utils.get_region()
    cfn = utils.get_all_cfn_outputs()

    # Descobre automaticamente usando as saídas do CloudFormation.
    # Tenta múltiplos nomes de output por compatibilidade com diferentes versões do template.
    gateway_role_arn = gateway_role_arn or cfn.get("GatewayRoleArn") or cfn.get("GatewayServiceRoleArn")
    rest_api_id = rest_api_id or cfn.get("ApiGatewayRestApiId") or cfn.get("TaskApiRestApiId")
    user_pool_id = user_pool_id or cfn.get("UserPoolId") or cfn.get("CognitoUserPoolId")
    cognito_client_id = cognito_client_id or cfn.get("UserPoolClientId") or cfn.get("CognitoClientId")

    if not gateway_role_arn:
        raise ValueError("gateway_role_arn not found. Check CFN outputs or pass explicitly.")
    if not rest_api_id:
        raise ValueError("rest_api_id not found. Check CFN outputs or pass explicitly.")

    client = boto3.client("bedrock-agentcore-control", region_name=region)

    utils.print_banner("AgentCore Gateway Setup")
    print(f"  Region       : {region}")
    print(f"  Gateway      : {gateway_name}")
    print(f"  REST API ID  : {rest_api_id}")
    print(f"  Auth mode    : {'CUSTOM_JWT' if use_jwt and user_pool_id else 'NONE'}")
    print()

    # --- Passo 1: Criar o Gateway ---
    # O Gateway é um proxy MCP que expõe APIs REST como ferramentas para o agente.
    # Ele traduz chamadas MCP (do Strands SDK) em chamadas REST (para a API de Tarefas).
    print("[1/2] Creating Gateway...")

    # Verifica se já existe um gateway com este nome (idempotência).
    try:
        paginator = client.get_paginator("list_gateways")
        for page in paginator.paginate():
            for gw in page.get("items", []):
                if gw["name"] == gateway_name:
                    gateway_id = gw["gatewayId"]
                    detail = client.get_gateway(gatewayIdentifier=gateway_id)
                    print(f"  ✅ Gateway already exists: {gateway_id}")
                    _ensure_target(client, gateway_id, rest_api_id)
                    gw_arn = detail.get("gatewayArn", "")
                    config = {
                        "gateway_id": gateway_id,
                        "gateway_url": detail.get("gatewayUrl", ""),
                        "gateway_arn": gw_arn,
                        "region": region,
                    }
                    utils.save_config("gateway", config)
                    return config
    except ClientError:
        pass

    # Monta os parâmetros de criação do Gateway.
    create_params = {
        "name": gateway_name,
        "description": "AgentCore Gateway for Aria workshop - routes MCP tool requests to backend APIs",
        "roleArn": gateway_role_arn,
        # protocolType: MCP (Model Context Protocol) — protocolo aberto para comunicação
        # entre modelos de IA e ferramentas externas.
        "protocolType": "MCP",
    }

    # Configuração de autenticação:
    # - CUSTOM_JWT: O Gateway valida o token JWT do Cognito antes de encaminhar a requisição.
    #   Necessário para que o Cedar Policy possa avaliar as permissões do usuário.
    # - NONE: Sem autenticação (útil para testes, mas não recomendado para produção).
    if use_jwt and user_pool_id and cognito_client_id:
        oidc_url = (
            f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
            f"/.well-known/openid-configuration"
        )
        create_params["authorizerType"] = "CUSTOM_JWT"
        create_params["authorizerConfiguration"] = {
            "customJWTAuthorizer": {
                "discoveryUrl": oidc_url,
                "allowedAudience": [cognito_client_id],
            }
        }
        print(f"  OIDC Discovery: {oidc_url}")
    else:
        create_params["authorizerType"] = "NONE"

    resp = client.create_gateway(**create_params)
    gateway_id = resp["gatewayId"]
    print(f"  Gateway ID: {gateway_id}")

    # Aguarda até ficar com status READY (a criação é assíncrona).
    utils.poll_until(
        describe_fn=lambda: client.get_gateway(gatewayIdentifier=gateway_id),
        label="Gateway",
        timeout=300,
    )

    detail = client.get_gateway(gatewayIdentifier=gateway_id)
    gateway_url = detail.get("gatewayUrl", "")
    gateway_arn = detail.get("gatewayArn", "")

    # --- Passo 2: Adicionar a API de Tarefas como um Target do Gateway ---
    _ensure_target(client, gateway_id, rest_api_id)

    # Salva as configurações para os próximos módulos usarem.
    config = {
        "gateway_id": gateway_id,
        "gateway_url": gateway_url,
        "gateway_arn": gateway_arn,
        "region": region,
    }
    utils.save_config("gateway", config)

    print()
    utils.print_banner("Gateway Setup Complete")
    print(f"  Gateway ID  : {gateway_id}")
    print(f"  Gateway URL : {gateway_url}")
    print(f"  Gateway ARN : {gateway_arn}")
    print()
    print(f"  export GATEWAY_ENDPOINT={gateway_url}")
    print()

    return config


def _ensure_target(client, gateway_id: str, rest_api_id: str) -> str:
    """Add Task API target to gateway. Idempotent."""
    # Um "Target" é uma API backend que o Gateway expõe como ferramentas MCP.
    # Aqui conectamos a API REST de Tarefas (criada pelo CloudFormation)
    # e definimos quais endpoints viram ferramentas do agente.
    print("[2/2] Adding Task API target...")

    try:
        resp = client.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name="TaskApi",
            description="Task Management REST API - CRUD operations for user tasks",
            targetConfiguration={
                "mcp": {
                    "apiGateway": {
                        "restApiId": rest_api_id,
                        "stage": "prod",
                        # toolOverrides: Define manualmente o nome e a descrição
                        # de cada ferramenta. O agente vê esses nomes e descrições
                        # e decide quando usar cada uma.
                        "apiGatewayToolConfiguration": {
                            "toolOverrides": [
                                {"path": "/tasks", "method": "GET", "name": "list_tasks",
                                 "description": "List all tasks for the current user"},
                                {"path": "/tasks", "method": "POST", "name": "create_task",
                                 "description": "Create a new task. Requires 'title' in JSON body."},
                                {"path": "/tasks/{id}", "method": "PUT", "name": "update_task",
                                 "description": "Update an existing task by ID."},
                                {"path": "/tasks/{id}", "method": "DELETE", "name": "delete_task",
                                 "description": "Delete a task by ID."},
                            ],
                            # toolFilters: Define quais endpoints e métodos HTTP são
                            # expostos como ferramentas. Endpoints não listados aqui
                            # ficam invisíveis para o agente.
                            "toolFilters": [
                                {"filterPath": "/tasks", "methods": ["GET", "POST"]},
                                {"filterPath": "/tasks/{id}", "methods": ["PUT", "DELETE"]},
                            ],
                        },
                    }
                }
            },
            # credentialProviderConfigurations: O Gateway usa sua própria IAM role
            # para chamar a API de Tarefas (via API Gateway). A identidade do USUÁRIO
            # é passada pelo JWT no header, não pelas credenciais da AWS.
            credentialProviderConfigurations=[
                {"credentialProviderType": "GATEWAY_IAM_ROLE"}
            ],
        )
        target_id = resp["targetId"]
        print(f"  Target ID: {target_id}")

        # Aguarda até o Target ficar pronto e operante.
        utils.poll_until(
            describe_fn=lambda: client.get_gateway_target(
                gatewayIdentifier=gateway_id, targetId=target_id
            ),
            label="Target",
            timeout=300,
        )
        return target_id

    except ClientError as e:
        if e.response["Error"]["Code"] in ("ConflictException", "ValidationException"):
            print("  ✅ Target already exists")
            return "existing"
        raise


if __name__ == "__main__":
    create_gateway()
