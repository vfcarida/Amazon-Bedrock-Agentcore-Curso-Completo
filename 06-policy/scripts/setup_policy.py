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
    return [
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
            "description": (
                "Permit creating tasks, but NOT with status 'completed'. "
                "Tasks must start as pending/in_progress."
            ),
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

    # Carrega as configurações salvas do gateway
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
    print("[1/3] Creating Policy Engine...")

    engine_id = None
    engine_arn = None

    # Verifica se já existe um gateway criado
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

    time.sleep(5)  # Dá um tempinho para as políticas se propagarem na rede

    # --- Passo 3: Conectar a política ao Gateway ---
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

    # Salva as configurações
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
