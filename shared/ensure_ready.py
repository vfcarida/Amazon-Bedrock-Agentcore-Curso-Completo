"""Smart catch-up / reconciliation script for AgentCore workshop.

This is the heart of the workshop's resilience. Call ensure_ready(module_id)
at the top of any notebook to guarantee that all prerequisite resources
are in place -- regardless of whether the learner:

  - Is starting fresh (nothing deployed)
  - Completed all prior modules cleanly
  - Skipped modules
  - Partially completed prior modules
  - Broke something in a prior module

The pattern is: DESCRIBE → ASSESS → ACT (idempotent).

Each resource type has:
  1. A describe function that checks current state
  2. An assess function that decides what action (if any) is needed
  3. An act function that creates/fixes the resource

All functions are safe to run multiple times.
"""

import json
import os
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from . import utils
from . import deploy_agent

# ---------------------------------------------------------------------------
# Nomes e descrições dos recursos
# ---------------------------------------------------------------------------


def _describe_runtime(control_client) -> dict | None:
    """Find the workshop runtime if it exists."""
    try:
        paginator = control_client.get_paginator("list_agent_runtimes")
        for page in paginator.paginate():
            for rt in page.get("agentRuntimes", page.get("agentRuntimeSummaries", [])):
                if rt.get("agentRuntimeName", "").startswith("aria_agent"):
                    detail = control_client.get_agent_runtime(
                        agentRuntimeId=rt["agentRuntimeId"]
                    )
                    return detail
    except ClientError:
        pass
    return None


def _describe_memory(control_client) -> dict | None:
    """Find the workshop memory resource if it exists."""
    try:
        paginator = control_client.get_paginator("list_memories")
        for page in paginator.paginate():
            for mem in page.get("memories", page.get("items", [])):
                if mem["id"].startswith("AriaMemory"):
                    detail = control_client.get_memory(memoryId=mem["id"])
                    return detail.get("memory", detail)
    except ClientError:
        pass
    return None


def _describe_gateway(control_client) -> dict | None:
    """Find the workshop gateway if it exists."""
    try:
        paginator = control_client.get_paginator("list_gateways")
        for page in paginator.paginate():
            for gw in page.get("items", []):
                if "aria" in gw.get("name", "").lower():
                    detail = control_client.get_gateway(
                        gatewayIdentifier=gw["gatewayId"]
                    )
                    return detail
    except ClientError:
        pass
    return None


def _describe_policy_engine(control_client) -> dict | None:
    """Find the workshop policy engine if it exists."""
    try:
        paginator = control_client.get_paginator("list_policy_engines")
        for page in paginator.paginate():
            for engine in page.get("policyEngines", page.get("items", [])):
                if "aria" in engine.get("name", "").lower():
                    detail = control_client.get_policy_engine(
                        policyEngineId=engine["policyEngineId"]
                    )
                    return detail
    except ClientError:
        pass
    return None


# ---------------------------------------------------------------------------
# Mapa de requisitos de cada módulo
# ---------------------------------------------------------------------------

# Cada módulo do curso diz quais recursos já devem estar rodando na AWS antes de começar
# "runtime" é especial -- quer dizer que não basta qualquer runtime, é preciso que o
# código do agente correspondente àquele módulo específico já esteja com deploy feito.

MODULE_REQUIREMENTS = {
    "00": [],                                               # Módulo 00: Valida os pré-requisitos do CloudFormation
    "01": [],                                               # Módulo 01: Introdução (nenhum recurso novo criado aqui)
    "02": [],                                               # Módulo 02: Onde criamos o Runtime pela primeira vez
    "03": ["runtime"],                                      # Módulo 03: Adicionando Ferramentas (requer o runtime já criado)
    "04": ["runtime"],                                      # Módulo 04: Memória
    "05": ["runtime", "memory"],                            # Módulo 05: Gateway e Identidade
    "06": ["runtime", "memory", "gateway"],                 # Módulo 06: Políticas de Acesso Cedar
    "07": ["runtime", "memory", "gateway", "policy"],       # Módulo 07: Observabilidade
    "08": ["runtime", "memory", "gateway", "policy"],       # Módulo 08: Deploy completo da aplicação
}


# ---------------------------------------------------------------------------
# Funções inteligentes de criação: elas só criam o recurso se ele não existir (são idempotentes)
# ---------------------------------------------------------------------------


def _ensure_memory(control_client) -> dict:
    """Ensure AgentCore Memory exists. Create if needed."""
    existing = _describe_memory(control_client)
    if existing and existing.get("status") in ("ACTIVE", "READY"):
        memory_id = existing["id"]
        print(f"  ✅ Memory already exists: {memory_id}")
        utils.save_config("memory", {
            "memory_id": memory_id,
            "region": utils.get_region(),
        })
        return existing

    if existing and existing.get("status") == "CREATING":
        print(f"  ⏳ Memory is still creating: {existing['id']}")
        memory_id = existing["id"]
    else:
        print("  🆕 Creating AgentCore Memory...")
        try:
            resp = control_client.create_memory(
                name="AriaMemory",
                description="Memory for Aria personal assistant workshop",
                eventExpiryDuration=90,
                memoryStrategies=[
                    {
                        "summaryMemoryStrategy": {
                            "name": "SessionSummarizer",
                            "description": "Summarizes conversation sessions",
                            "namespaces": ["/summaries/{actorId}/{sessionId}"],
                        }
                    },
                    {
                        "userPreferenceMemoryStrategy": {
                            "name": "PreferenceLearner",
                            "description": "Learns user preferences",
                            "namespaces": ["/preferences/{actorId}"],
                        }
                    },
                    {
                        "semanticMemoryStrategy": {
                            "name": "FactExtractor",
                            "description": "Extracts factual information",
                            "namespaces": ["/facts/{actorId}"],
                        }
                    },
                ],
            )
            memory_id = resp["memory"]["id"]
        except ClientError as e:
            if e.response["Error"]["Code"] in ("ConflictException", "ValidationException"):
                print("  ⚠ Memory conflict -- searching for existing...")
                existing = _describe_memory(control_client)
                if existing:
                    memory_id = existing["id"]
                else:
                    raise
            else:
                raise

    # Aguarda até que o status fique como ACTIVE
    result = utils.poll_until(
        describe_fn=lambda: control_client.get_memory(memoryId=memory_id).get("memory", {}),
        target_statuses={"ACTIVE"},
        label="Memory",
        timeout=300,
    )

    print(f"  ✅ Memory ready: {memory_id}")
    utils.save_config("memory", {
        "memory_id": memory_id,
        "region": utils.get_region(),
    })
    return result


def _ensure_gateway(control_client) -> dict:
    """Ensure AgentCore Gateway exists with Task API target. Create if needed."""
    cfn = utils.get_all_cfn_outputs()
    rest_api_id = cfn.get("ApiGatewayRestApiId") or cfn.get("TaskApiRestApiId")
    gateway_role_arn = cfn.get("GatewayRoleArn") or cfn.get("GatewayServiceRoleArn")

    if not rest_api_id or not gateway_role_arn:
        raise RuntimeError(
            "Cannot create Gateway: missing ApiGatewayRestApiId or GatewayRoleArn "
            "from CFN outputs. Ensure the prerequisites stack is deployed."
        )

    # Busca os detalhes do Cognito gerados no CloudFormation (necessário pro login com CUSTOM_JWT)
    user_pool_id = cfn.get("UserPoolId") or cfn.get("CognitoUserPoolId")
    cognito_client_id = cfn.get("UserPoolClientId") or cfn.get("CognitoClientId")

    existing = _describe_gateway(control_client)
    if existing and existing.get("status") in ("READY", "ACTIVE"):
        gateway_id = existing["gatewayId"]
        print(f"  ✅ Gateway already exists: {gateway_id}")
        gw_arn = existing.get("gatewayArn", "")
        utils.save_config("gateway", {
            "gateway_id": gateway_id,
            "gateway_url": existing.get("gatewayUrl", ""),
            "gateway_arn": gw_arn,
            "region": utils.get_region(),
        })
        return existing

    # Cria o Gateway
    print("  🆕 Creating AgentCore Gateway...")
    region = utils.get_region()

    create_params = {
        "name": "aria-gateway",
        "description": "AgentCore Gateway for Aria workshop",
        "roleArn": gateway_role_arn,
        "protocolType": "MCP",
    }

    # Se tiver Cognito configurado, usa CUSTOM_JWT, senão deixa liberado (NONE)
    if user_pool_id and cognito_client_id:
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
        print(f"  Using CUSTOM_JWT auth (Cognito: {user_pool_id})")
    else:
        create_params["authorizerType"] = "NONE"
        print("  Using NONE auth (Cognito not found in CFN outputs)")

    try:
        resp = control_client.create_gateway(**create_params)
    except ClientError as e:
        if e.response["Error"]["Code"] in ("ConflictException", "ValidationException"):
            print("  ⚠ Gateway conflict -- searching for existing...")
            existing = _describe_gateway(control_client)
            if existing:
                gateway_id = existing["gatewayId"]
                resp = existing
            else:
                raise
        else:
            raise

    gateway_id = resp.get("gatewayId", resp.get("gatewayIdentifier"))

    # Aguarda até ficar com status READY
    utils.poll_until(
        describe_fn=lambda: control_client.get_gateway(gatewayIdentifier=gateway_id),
        label="Gateway",
        timeout=300,
    )

    gw_detail = control_client.get_gateway(gatewayIdentifier=gateway_id)
    gateway_url = gw_detail.get("gatewayUrl", "")
    gateway_arn = gw_detail.get("gatewayArn", "")

    # Adiciona a API de Tarefas como um target no gateway
    print("  📎 Adding Task API target...")
    try:
        target_resp = control_client.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name="TaskApi",
            description="Task Management REST API for Aria workshop",
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
        target_id = target_resp["targetId"]

        # Aguarda até o Target ficar pronto e operante
        utils.poll_until(
            describe_fn=lambda: control_client.get_gateway_target(
                gatewayIdentifier=gateway_id, targetId=target_id
            ),
            label="Gateway Target",
            timeout=300,
        )
        print(f"  ✅ Target ready: {target_id}")
    except ClientError as e:
        if e.response["Error"]["Code"] in ("ConflictException", "ValidationException"):
            print("  ✅ Target already exists")
            target_id = "existing"
        else:
            raise

    config = {
        "gateway_id": gateway_id,
        "gateway_url": gateway_url,
        "gateway_arn": gateway_arn,
        "region": utils.get_region(),
    }
    utils.save_config("gateway", config)
    print(f"  ✅ Gateway ready: {gateway_id}")
    return gw_detail


def _ensure_policy(control_client) -> dict:
    """Ensure Policy Engine exists with Cedar policies. Create if needed."""
    gw_config = utils.load_config("gateway")
    if not gw_config:
        raise RuntimeError("Gateway config not found. Ensure gateway is set up first.")

    gateway_id = gw_config["gateway_id"]
    gateway_arn = gw_config.get("gateway_arn", "")

    existing = _describe_policy_engine(control_client)
    if existing and existing.get("status") in ("ACTIVE", "READY"):
        engine_id = existing["policyEngineId"]
        print(f"  ✅ Policy Engine already exists: {engine_id}")
        utils.save_config("policy", {
            "policy_engine_id": engine_id,
            "policy_engine_arn": existing.get("policyEngineArn", ""),
            "gateway_id": gateway_id,
            "region": utils.get_region(),
        })
        return existing

    # Cria a engine do Policy
    print("  🆕 Creating Policy Engine...")
    try:
        resp = control_client.create_policy_engine(
            name="aria_policy_engine",
            description="Policy engine for Aria workshop - Cedar policy enforcement",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] in ("ConflictException", "ValidationException"):
            print("  ⚠ Policy engine conflict -- searching for existing...")
            existing = _describe_policy_engine(control_client)
            if existing:
                engine_id = existing["policyEngineId"]
                engine_arn = existing.get("policyEngineArn", "")
            else:
                raise
        else:
            raise
    else:
        engine_id = resp["policyEngineId"]
        engine_arn = resp.get("policyEngineArn", "")

    # Aguarda até que o status fique como ACTIVE
    utils.poll_until(
        describe_fn=lambda: control_client.get_policy_engine(policyEngineId=engine_id),
        target_statuses={"ACTIVE", "READY"},
        label="Policy Engine",
        timeout=300,
    )

    # Cria as regras de acesso Cedar separadas por ação
    policies = [
        {
            "name": "permit_list_tasks",
            "description": "Permit listing tasks. Blocks listing only completed tasks.",
            "cedar": (
                f'permit(\n'
                f'  principal,\n'
                f'  action == AgentCore::Action::"TaskApi___list_tasks",\n'
                f'  resource == AgentCore::Gateway::"{gateway_arn}"\n'
                f') when {{\n'
                f'  !(context.input has status && context.input.status == "completed")\n'
                f'}};\n'
            ),
        },
        {
            "name": "permit_create_task",
            "description": "Permit creating tasks, but NOT with status completed.",
            "cedar": (
                f'permit(\n'
                f'  principal,\n'
                f'  action == AgentCore::Action::"TaskApi___create_task",\n'
                f'  resource == AgentCore::Gateway::"{gateway_arn}"\n'
                f') when {{\n'
                f'  !(context.input has status && context.input.status == "completed")\n'
                f'}};\n'
            ),
        },
        {
            "name": "permit_update_task",
            "description": "Permit all task updates including setting status to completed.",
            "cedar": (
                f'permit(\n'
                f'  principal,\n'
                f'  action == AgentCore::Action::"TaskApi___update_task",\n'
                f'  resource == AgentCore::Gateway::"{gateway_arn}"\n'
                f') when {{\n'
                f'  !(context.input has status && context.input.status == "__blocked__")\n'
                f'}};\n'
            ),
        },
        {
            "name": "permit_delete_task",
            "description": "Permit deleting tasks by ID.",
            "cedar": (
                f'permit(\n'
                f'  principal,\n'
                f'  action == AgentCore::Action::"TaskApi___delete_task",\n'
                f'  resource == AgentCore::Gateway::"{gateway_arn}"\n'
                f') when {{\n'
                f'  !(context.input has id && context.input.id == "__blocked__")\n'
                f'}};\n'
            ),
        },
    ]
    for p in policies:
        try:
            control_client.create_policy(
                policyEngineId=engine_id,
                name=p["name"],
                description=p["description"],
                definition={"cedar": {"statement": p["cedar"]}},
            )
            print(f"    Created policy: {p['name']}")
        except ClientError as e:
            if e.response["Error"]["Code"] in ("ConflictException", "ValidationException"):
                print(f"    Policy already exists: {p['name']}")
            else:
                raise

    # Prende o motor de políticas lá no Gateway
    print("  📎 Attaching policy engine to gateway...")
    try:
        gw = control_client.get_gateway(gatewayIdentifier=gateway_id)
        update_params = {
            "gatewayIdentifier": gateway_id,
            "name": gw["name"],
            "roleArn": gw["roleArn"],
            "protocolType": gw["protocolType"],
            "authorizerType": gw["authorizerType"],
            "policyEngineConfiguration": {
                "arn": engine_arn,
                "mode": "ENFORCE",
            },
        }
        if "authorizerConfiguration" in gw:
            update_params["authorizerConfiguration"] = gw["authorizerConfiguration"]

        control_client.update_gateway(**update_params)
        print("  ✅ Policy engine attached in ENFORCE mode")
    except ClientError as e:
        print(f"  ⚠ Could not attach policy engine: {e}")

    config = {
        "policy_engine_id": engine_id,
        "policy_engine_arn": engine_arn,
        "gateway_id": gateway_id,
        "region": utils.get_region(),
    }
    utils.save_config("policy", config)
    return {"policyEngineId": engine_id, "policyEngineArn": engine_arn}


def _ensure_runtime(control_client, module_id: str) -> dict:
    """Ensure the correct agent version is deployed to Runtime.

    Deploys the agent code from the appropriate module directory.
    """
    # Mapeia a pasta do código do agente referente a este módulo
    module_agent_dirs = {
        "02": "02-runtime",
        "03": "03-tools",
        "04": "04-memory",
        "05": "05-gateway-identity",
        "06": "05-gateway-identity",  # Reutiliza o código do agente da pasta 05
        "07": "07-observability-evaluations",
        "08": "07-observability-evaluations",  # Reutiliza o código do agente da pasta 07
    }

    # Quando estiver fazendo catch-up para um lab específico, ele vai fazer o deploy
    # do código do agente da versão imediatamente ANTERIOR àquele lab.
    prev_modules = {
        "03": "02", "04": "03", "05": "04",
        "06": "05", "07": "05", "08": "07",
    }

    target_module = prev_modules.get(module_id, module_id)
    agent_subdir = module_agent_dirs.get(target_module)
    if not agent_subdir:
        return {}

    agent_dir = utils.WORKSHOP_DIR / agent_subdir / "agent"
    if not agent_dir.exists():
        print(f"  ⚠ Agent directory not found: {agent_dir}")
        return {}

    # Confere se o Runtime já está rodando e saudável
    existing = _describe_runtime(control_client)
    if existing and existing.get("status") == "READY":
        print(f"  ✅ Runtime already exists and is READY: {existing['agentRuntimeId']}")
        # Salva as configurações
        result = {
            "runtime_id": existing["agentRuntimeId"],
            "runtime_arn": existing.get("agentRuntimeArn", ""),
            "runtime_name": existing.get("agentRuntimeName", ""),
            "status": "READY",
            "region": utils.get_region(),
            "account_id": utils.get_account_id(),
        }
        utils.save_config("runtime", result)
        return result

    # Ops, precisamos fazer um novo deploy para seguir adiante
    print(f"  🆕 Deploying agent from {agent_subdir}/agent...")

    # Constrói as variáveis de ambiente baseadas nos módulos que já foram configurados
    env_vars = {}
    memory_config = utils.load_config("memory")
    if memory_config:
        env_vars["MEMORY_ID"] = memory_config["memory_id"]
    gateway_config = utils.load_config("gateway")
    if gateway_config:
        env_vars["GATEWAY_ENDPOINT"] = gateway_config.get("gateway_url", "")

    return deploy_agent.deploy(
        agent_dir=str(agent_dir),
        env_vars=env_vars,
    )


# ---------------------------------------------------------------------------
# Ponto de entrada principal do script
# ---------------------------------------------------------------------------


def ensure_ready(module_id: str) -> dict:
    """Ensure all prerequisites for the given module are in place.

    This is the function to call at the top of every notebook:

        from shared.ensure_ready import ensure_ready
        config = ensure_ready("04")  # Especificamente para o módulo Memory

    It will:
    1. Check CloudFormation prerequisites
    2. Describe all existing AgentCore resources
    3. Create/fix any missing prerequisites for the requested module
    4. Return a dict with all resource IDs and endpoints

    Args:
        module_id: The module being started (e.g., "02", "05").

    Returns:
        Dict with all discovered/created resource configurations.
    """
    utils.print_banner(f"Ensuring prerequisites for Module {module_id}")
    print()

    region = utils.get_region()
    control_client = boto3.client("bedrock-agentcore-control", region_name=region)

    requirements = MODULE_REQUIREMENTS.get(module_id, [])
    result = {"module": module_id, "region": region}

    # Sempre verifica se a base do CloudFormation está pronta
    print("📋 Checking CloudFormation outputs...")
    cfn = utils.get_all_cfn_outputs()
    if cfn:
        print(f"  ✅ Found {len(cfn)} outputs from CFN stacks")
        result["cfn_outputs"] = cfn
    else:
        print("  ⚠ No CFN outputs found -- some features may not work")

    # Cria ou checa todos os recursos que a aula de hoje exige
    if "memory" in requirements:
        print()
        print("🧠 Checking Memory...")
        try:
            mem = _ensure_memory(control_client)
            mem_config = utils.load_config("memory")
            if mem_config:
                result["memory_id"] = mem_config["memory_id"]
        except Exception as e:
            print(f"  ❌ Memory setup failed: {e}")

    if "gateway" in requirements:
        print()
        print("🌐 Checking Gateway...")
        try:
            gw = _ensure_gateway(control_client)
            gw_config = utils.load_config("gateway")
            if gw_config:
                result["gateway_id"] = gw_config["gateway_id"]
                result["gateway_url"] = gw_config.get("gateway_url", "")
        except Exception as e:
            print(f"  ❌ Gateway setup failed: {e}")

    if "policy" in requirements:
        print()
        print("🛡 Checking Policy Engine...")
        try:
            pol = _ensure_policy(control_client)
            pol_config = utils.load_config("policy")
            if pol_config:
                result["policy_engine_id"] = pol_config["policy_engine_id"]
        except Exception as e:
            print(f"  ❌ Policy setup failed: {e}")

    if "runtime" in requirements:
        print()
        print("🚀 Checking Runtime...")
        try:
            rt = _ensure_runtime(control_client, module_id)
            rt_config = utils.load_config("runtime")
            if rt_config:
                result["runtime_id"] = rt_config.get("runtime_id", "")
                result["runtime_arn"] = rt_config.get("runtime_arn", "")
        except Exception as e:
            print(f"  ❌ Runtime setup failed: {e}")

    print()
    utils.print_banner(f"Module {module_id} Ready")
    print()

    return result
