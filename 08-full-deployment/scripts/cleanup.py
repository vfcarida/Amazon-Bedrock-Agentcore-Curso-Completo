"""Cleanup script for all AgentCore workshop resources.

Deletes Runtime, Memory, Gateway, Policy Engine resources created during
the workshop. CloudFormation stacks are managed separately by Workshop Studio.

Run from notebook or command line:
    python cleanup.py [--yes]

This script is safe to run multiple times - it handles already-deleted resources.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import utils

import boto3
from botocore.exceptions import ClientError


def cleanup(auto_confirm: bool = False) -> None:
    """Delete all AgentCore workshop resources.

    Args:
        auto_confirm: Skip confirmation prompt if True.
    """
    region = utils.get_region()

    utils.print_banner("AgentCore Workshop Cleanup")
    print(f"  Region: {region}")
    print()

    # Gather what exists
    resources = []
    runtime_config = utils.load_config("runtime")
    memory_config = utils.load_config("memory")
    gateway_config = utils.load_config("gateway")
    policy_config = utils.load_config("policy")
    evals_config = utils.load_config("evaluations")

    if runtime_config:
        print(f"  Found: Runtime  → {runtime_config.get('runtime_id', '?')}")
        resources.append(("runtime", runtime_config))
    if policy_config:
        print(f"  Found: Policy   → {policy_config.get('policy_engine_id', '?')}")
        resources.append(("policy", policy_config))
    if gateway_config:
        print(f"  Found: Gateway  → {gateway_config.get('gateway_id', '?')}")
        resources.append(("gateway", gateway_config))
    if memory_config:
        print(f"  Found: Memory   → {memory_config.get('memory_id', '?')}")
        resources.append(("memory", memory_config))

    if not resources:
        print("  No saved configurations found. Nothing to clean up.")
        print("  If resources exist, delete them via the AWS Console.")
        return

    print()

    if not auto_confirm:
        confirm = input("  Proceed with deletion? [y/N] ")
        if confirm.lower() != "y":
            print("  Cancelled.")
            return

    control_client = boto3.client("bedrock-agentcore-control", region_name=region)

    # Delete in reverse dependency order
    for resource_type, config in resources:
        try:
            if resource_type == "runtime":
                _delete_runtime(control_client, config)
            elif resource_type == "policy":
                _delete_policy(control_client, config)
            elif resource_type == "gateway":
                _delete_gateway(control_client, config)
            elif resource_type == "memory":
                _delete_memory(control_client, config)
        except Exception as e:
            print(f"  ⚠ Error cleaning {resource_type}: {e}")

    # Clean up config files
    config_dir = utils.CONFIG_DIR
    if config_dir.exists():
        for f in config_dir.glob("*.json"):
            f.unlink()
            print(f"  Removed config: {f.name}")

    print()
    utils.print_banner("Cleanup Complete")
    print("  AgentCore resource deletion initiated.")
    print("  Deletions may take a few minutes to complete.")
    print()


def _delete_runtime(client, config: dict) -> None:
    """Delete an AgentCore Runtime."""
    runtime_id = config.get("runtime_id")
    if not runtime_id:
        return

    print(f"  🗑 Deleting Runtime: {runtime_id}")
    try:
        client.delete_agent_runtime(agentRuntimeId=runtime_id)
        print("    Deletion initiated.")
    except ClientError as e:
        if "NotFound" in str(e) or "ResourceNotFound" in str(e):
            print("    Already deleted.")
        else:
            print(f"    Error: {e}")


def _delete_policy(client, config: dict) -> None:
    """Delete a Policy Engine and its policies."""
    engine_id = config.get("policy_engine_id")
    if not engine_id:
        return

    print(f"  🗑 Deleting Policy Engine: {engine_id}")

    # Delete policies first
    try:
        paginator = client.get_paginator("list_policies")
        for page in paginator.paginate(policyEngineId=engine_id):
            for policy in page.get("items", []):
                policy_id = policy["policyId"]
                client.delete_policy(policyEngineId=engine_id, policyId=policy_id)
                print(f"    Deleted policy: {policy_id}")
    except ClientError as e:
        print(f"    Warning deleting policies: {e}")

    try:
        client.delete_policy_engine(policyEngineIdentifier=engine_id)
        print("    Engine deletion initiated.")
    except ClientError as e:
        if "NotFound" in str(e):
            print("    Already deleted.")
        else:
            print(f"    Error: {e}")


def _delete_gateway(client, config: dict) -> None:
    """Delete an AgentCore Gateway and its targets."""
    gateway_id = config.get("gateway_id")
    if not gateway_id:
        return

    print(f"  🗑 Deleting Gateway: {gateway_id}")

    # Delete targets first
    try:
        paginator = client.get_paginator("list_gateway_targets")
        for page in paginator.paginate(gatewayIdentifier=gateway_id):
            for target in page.get("items", []):
                target_id = target["targetId"]
                client.delete_gateway_target(
                    gatewayIdentifier=gateway_id, targetId=target_id
                )
                print(f"    Deleted target: {target_id}")
    except ClientError as e:
        print(f"    Warning deleting targets: {e}")

    try:
        client.delete_gateway(gatewayIdentifier=gateway_id)
        print("    Gateway deletion initiated.")
    except ClientError as e:
        if "NotFound" in str(e):
            print("    Already deleted.")
        else:
            print(f"    Error: {e}")


def _delete_memory(client, config: dict) -> None:
    """Delete an AgentCore Memory resource."""
    memory_id = config.get("memory_id")
    if not memory_id:
        return

    print(f"  🗑 Deleting Memory: {memory_id}")
    try:
        client.delete_memory(memoryId=memory_id)
        print("    Deletion initiated.")
    except ClientError as e:
        if "NotFound" in str(e):
            print("    Already deleted.")
        else:
            print(f"    Error: {e}")


if __name__ == "__main__":
    auto = "--yes" in sys.argv or "-y" in sys.argv
    cleanup(auto_confirm=auto)
