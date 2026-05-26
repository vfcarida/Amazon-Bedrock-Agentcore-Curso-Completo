"""Setup AgentCore Policy Engine with Cedar policies.

Creates a Policy Engine, adds per-action Cedar permit policies for each
Gateway tool, and attaches it to the existing Gateway in ENFORCE mode.

Run from notebook or command line:
    python setup_policy.py

Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-policy.html

Cedar policy design notes:
  - Each tool gets its own permit policy with a condition on context.input fields.
  - Broad permits cause tools to disappear in ENFORCE mode.
  - Forbid policies are rejected as "Overly Restrictive".
  - Gateway must use CUSTOM_JWT for ENFORCE mode.
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import utils

import boto3
from botocore.exceptions import ClientError


def get_cedar_policies(gateway_arn: str) -> list[dict]:
    """Return the Cedar policy definitions for the Task API.

    Each policy permits a single action with a condition on context.input
    fields. The business rule: tasks cannot be created with status "completed".

    Args:
        gateway_arn: The ARN of the Gateway (used as the Cedar resource).

    Returns:
        List of policy definition dicts.
    """
    # IMPORTANTE: Por que uma política por ação (e não uma política geral)?
    # No modo ENFORCE do AgentCore, se uma ferramenta NÃO tem uma política
    # "permit" explícita, ela simplesmente desaparece da lista de ferramentas
    # do agente. Ou seja: sem política = ferramenta invisível.
    #
    # Além disso, políticas "forbid" são rejeitadas como "Overly Restrictive".
    # A solução é: criar uma política "permit" para cada ação, com condições
    # que bloqueiam os casos indesejados (usando negação no "when").
    return [
        {
            "name": "permit_list_tasks",
            "description": "Permit listing tasks. Blocks listing only completed tasks.",
            # Regra: Permite listar tarefas, EXCETO se o filtro for apenas tarefas
            # com status "completed". Isso evita que o agente busque apenas tarefas
            # já concluídas (o que seria inútil e custoso).
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
            "description": (
                "Permit creating tasks, but NOT with status 'completed'. "
                "Tasks must start as pending/in_progress."
            ),
            # Regra de negócio: Tarefas não podem ser CRIADAS com status "completed".
            # Elas devem começar como "pending" ou "in_progress" e só podem ser
            # marcadas como "completed" via update (permit_update_task).
            # Isso garante que o fluxo de trabalho seja respeitado.
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
            "description": "Permit all task updates (including setting status to completed).",
            # Regra: Permite qualquer atualização de tarefa.
            # A condição "__blocked__" é um placeholder que nunca é ativado —
            # serve apenas para satisfazer o formato obrigatório de condição do Cedar.
            # Na prática, todas as atualizações são permitidas.
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
            # Regra: Permite deletar qualquer tarefa.
            # Mesma técnica do update — "__blocked__" nunca ocorre na prática.
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


def create_policy_engine(
    engine_name: str = "aria_policy_engine",
    enforcement_mode: str = "ENFORCE",
) -> dict:
    """Create a Policy Engine with Cedar policies and attach to Gateway. Idempotent.

    Returns:
        Dict with policy_engine_id, policy_engine_arn, gateway_id.
    """
    region = utils.get_region()
    client = boto3.client("bedrock-agentcore-control", region_name=region)

    # Carrega as configurações salvas do gateway (necessário para saber o ARN).
    gw_config = utils.get_gateway_config(client)
    gateway_id = gw_config["gateway_id"]
    gateway_arn = gw_config["gateway_arn"]

    utils.print_banner("AgentCore Policy Setup")
    print(f"  Region           : {region}")
    print(f"  Policy Engine    : {engine_name}")
    print(f"  Gateway ID       : {gateway_id}")
    print(f"  Enforcement Mode : {enforcement_mode}")
    print()

    # --- Passo 1: Criar o Policy Engine (Motor de Políticas) ---
    # O Policy Engine é o recurso que armazena e avalia as políticas Cedar.
    # Ele funciona como um "guardião" que decide se cada chamada de ferramenta
    # deve ser permitida ou bloqueada.
    print("[1/3] Creating Policy Engine...")

    engine_id = None
    engine_arn = None

    # Verifica se já existe um Policy Engine com este nome.
    try:
        paginator = client.get_paginator("list_policy_engines")
        for page in paginator.paginate():
            for engine in page.get("policyEngines", page.get("items", [])):
                if engine["name"] == engine_name:
                    engine_id = engine["policyEngineId"]
                    detail = client.get_policy_engine(policyEngineId=engine_id)
                    engine_arn = detail.get("policyEngineArn", "")
                    print(f"  ✅ Policy Engine already exists: {engine_id}")
                    break
            if engine_id:
                break
    except ClientError:
        pass

    if not engine_id:
        try:
            resp = client.create_policy_engine(
                name=engine_name,
                description="Policy engine for Aria workshop - Cedar policy enforcement",
            )
            engine_id = resp["policyEngineId"]
            engine_arn = resp.get("policyEngineArn", "")
            print(f"  Engine ID: {engine_id}")

            # Aguarda até que o status fique como ACTIVE.
            utils.poll_until(
                describe_fn=lambda: client.get_policy_engine(policyEngineId=engine_id),
                target_statuses={"ACTIVE", "READY"},
                label="Policy Engine",
                timeout=300,
            )
        except ClientError as e:
            if e.response["Error"]["Code"] in ("ConflictException", "ValidationException"):
                print(f"  ⚠ Engine conflict: {e}")
                raise
            raise

    # --- Passo 2: Criar as Políticas Cedar ---
    # Cada política é uma regra escrita na linguagem Cedar que define
    # se uma ação específica deve ser permitida ou bloqueada.
    # O formato é: permit(principal, action, resource) when { condição };
    print()
    print("[2/3] Creating Cedar policies...")

    policies = get_cedar_policies(gateway_arn)
    for p in policies:
        try:
            resp = client.create_policy(
                policyEngineId=engine_id,
                name=p["name"],
                description=p["description"],
                definition={"cedar": {"statement": p["cedar"]}},
            )
            print(f"  ✅ Created: {p['name']} (ID: {resp['policyId']})")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                print(f"  ✅ Already exists: {p['name']}")
            else:
                raise

    # Dá um tempinho para as políticas se propagarem na rede interna da AWS.
    time.sleep(5)

    # --- Passo 3: Conectar o Policy Engine ao Gateway ---
    # Existem dois modos de enforcement:
    # - MONITOR: Avalia as políticas mas NÃO bloqueia (só loga). Útil para testes.
    # - ENFORCE: Avalia as políticas E bloqueia chamadas não permitidas. Para produção.
    print()
    print(f"[3/3] Attaching to gateway (mode: {enforcement_mode})...")

    gw = client.get_gateway(gatewayIdentifier=gateway_id)
    update_params = {
        "gatewayIdentifier": gateway_id,
        "name": gw["name"],
        "roleArn": gw["roleArn"],
        "protocolType": gw["protocolType"],
        "authorizerType": gw["authorizerType"],
        "policyEngineConfiguration": {
            "arn": engine_arn,
            "mode": enforcement_mode,
        },
    }
    if "authorizerConfiguration" in gw:
        update_params["authorizerConfiguration"] = gw["authorizerConfiguration"]

    client.update_gateway(**update_params)
    print(f"  ✅ Policy engine attached in {enforcement_mode} mode")

    # Salva as configurações para os próximos módulos usarem.
    config = {
        "policy_engine_id": engine_id,
        "policy_engine_arn": engine_arn,
        "gateway_id": gateway_id,
        "enforcement_mode": enforcement_mode,
        "region": region,
    }
    utils.save_config("policy", config)

    print()
    utils.print_banner("Policy Setup Complete")
    print(f"  Engine ID  : {engine_id}")
    print(f"  Engine ARN : {engine_arn}")
    print(f"  Gateway    : {gateway_id}")
    print(f"  Mode       : {enforcement_mode}")
    print()
    print("  Business rule enforced:")
    print("    Tasks cannot be created with status 'completed'.")
    print("    They must start as 'pending' or 'in_progress'.")
    print()

    return config


# Também salva os arquivos Cedar separadamente para referência
def write_cedar_files(gateway_arn: str, output_dir: str | None = None) -> None:
    """Write Cedar policy files to disk for reference."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "policies")

    os.makedirs(output_dir, exist_ok=True)

    for p in get_cedar_policies(gateway_arn):
        path = os.path.join(output_dir, f"{p['name']}.cedar")
        with open(path, "w") as f:
            f.write(f"// {p['description']}\n")
            f.write(f"// Auto-generated for Gateway: {gateway_arn}\n\n")
            f.write(p["cedar"])
        print(f"  Wrote: {path}")


if __name__ == "__main__":
    create_policy_engine()
