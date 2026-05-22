"""Setup AgentCore Memory for the Aria agent.

Creates a Memory resource with three long-term memory strategies:
- SessionSummarizer: Conversation session summaries
- PreferenceLearner: User preference extraction
- FactExtractor: Semantic fact extraction

Run from notebook or command line:
    python setup_memory.py

Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-memory.html
"""

import sys
import os

# Allow imports from shared/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import utils

import boto3
from botocore.exceptions import ClientError


def create_memory(region: str | None = None) -> dict:
    """Create an AgentCore Memory resource. Idempotent.

    Returns:
        Dict with memory_id, region, and strategies.
    """
    region = region or utils.get_region()
    client = boto3.client("bedrock-agentcore-control", region_name=region)

    utils.print_banner("Creating AgentCore Memory")
    print()

    # Check if it already exists
    try:
        paginator = client.get_paginator("list_memories")
        for page in paginator.paginate():
            for mem in page.get("memories", page.get("items", [])):
                if mem["id"].startswith("AriaMemory"):
                    memory_id = mem["id"]
                    detail = client.get_memory(memoryId=memory_id)
                    memory = detail.get("memory", detail)
                    if memory.get("status") in ("ACTIVE", "READY"):
                        print(f"✅ AriaMemory already exists: {memory_id}")
                        config = {"memory_id": memory_id, "region": region}
                        utils.save_config("memory", config)
                        return config
    except ClientError:
        pass

    # Create new memory
    print("Creating Memory resource with LTM strategies...")
    try:
        resp = client.create_memory(
            name="AriaMemory",
            description=(
                "Memory for Aria personal assistant - supports conversation "
                "persistence and long-term user knowledge"
            ),
            eventExpiryDuration=90,
            memoryStrategies=[
                {
                    "summaryMemoryStrategy": {
                        "name": "SessionSummarizer",
                        "description": "Summarizes conversation sessions for quick context retrieval",
                        "namespaces": ["/summaries/{actorId}/{sessionId}"],
                    }
                },
                {
                    "userPreferenceMemoryStrategy": {
                        "name": "PreferenceLearner",
                        "description": "Learns and stores user preferences across sessions",
                        "namespaces": ["/preferences/{actorId}"],
                    }
                },
                {
                    "semanticMemoryStrategy": {
                        "name": "FactExtractor",
                        "description": "Extracts and stores factual information from conversations",
                        "namespaces": ["/facts/{actorId}"],
                    }
                },
            ],
        )
    except ClientError as e:
        if e.response["Error"]["Code"] in ("ConflictException", "ValidationException"):
            print("⚠ AriaMemory already exists but wasn't found in listing.")
            print("  This can happen due to eventual consistency.")
            print("  Provide the memory ID manually if needed.")
            raise
        raise

    memory_id = resp["memory"]["id"]
    print(f"Memory ID: {memory_id}")

    # Wait for ACTIVE
    print("Waiting for memory to become ACTIVE...")
    utils.poll_until(
        describe_fn=lambda: client.get_memory(memoryId=memory_id).get("memory", {}),
        target_statuses={"ACTIVE"},
        label="Memory",
        timeout=300,
    )

    config = {
        "memory_id": memory_id,
        "region": region,
        "strategies": ["SessionSummarizer", "PreferenceLearner", "FactExtractor"],
    }
    utils.save_config("memory", config)

    print()
    utils.print_banner("Memory Setup Complete")
    print(f"  Memory ID: {memory_id}")
    print()
    print("  Strategies:")
    print("    - SessionSummarizer → /summaries/{actorId}/{sessionId}")
    print("    - PreferenceLearner → /preferences/{actorId}")
    print("    - FactExtractor     → /facts/{actorId}")
    print()
    print(f"  export MEMORY_ID={memory_id}")
    print()

    return config


if __name__ == "__main__":
    create_memory()
