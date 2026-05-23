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

    # Descobre automaticamente usando as saídas do CloudFormation
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
    print("[1/2] Creating Gateway...")

    # Verifica se já existe um gateway criado
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

    create_params = {
        "name": gateway_name,
        "description": "AgentCore Gateway for Aria workshop - routes MCP tool requests to backend APIs",
        "roleArn": gateway_role_arn,
        "protocolType": "MCP",
    }

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

    # Aguarda até ficar com status READY
    utils.poll_until(
        describe_fn=lambda: client.get_gateway(gatewayIdentifier=gateway_id),
        label="Gateway",
        timeout=300,
    )

    detail = client.get_gateway(gatewayIdentifier=gateway_id)
    gateway_url = detail.get("gatewayUrl", "")
    gateway_arn = detail.get("gatewayArn", "")

    # --- Passo 2: Adicionar um Target ---
    _ensure_target(client, gateway_id, rest_api_id)

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
                            "toolFilters": [
                                {"filterPath": "/tasks", "methods": ["GET", "POST"]},
                                {"filterPath": "/tasks/{id}", "methods": ["PUT", "DELETE"]},
                            ],
                        },
                    }
                }
            },
            credentialProviderConfigurations=[
                {"credentialProviderType": "GATEWAY_IAM_ROLE"}
            ],
        )
        target_id = resp["targetId"]
        print(f"  Target ID: {target_id}")

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
