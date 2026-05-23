"""
Lambda handler for GET /history/{sessionId}.

Retrieves the conversation events for a specific session from AgentCore Memory
using the list_events API. Events contain the full message payload (role, content)
stored by the Strands AgentCoreMemorySessionManager.

The user ID is extracted from the Cognito JWT claims for tenant-scoped access.
"""

import json
import os

import boto3

MEMORY_ID = os.environ.get("MEMORY_ID", "")
REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_user_id(event: dict) -> str:
    """Extract the user ID (sub) from the Cognito JWT claims."""
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    return claims.get("sub", "unknown")


def extract_text_from_content(content_blocks):
    """Extract plain text from a Bedrock message content array."""
    parts = []
    for block in content_blocks:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict):
            if "text" in block:
                parts.append(block["text"])
    return "\n".join(parts)


def handler(event, context):
    user_id = get_user_id(event)
    session_id = event.get("pathParameters", {}).get("sessionId")

    if not session_id:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": "sessionId path parameter is required"}),
        }

    try:
        client = boto3.client("bedrock-agentcore", region_name=REGION)

        # Pega o histórico de eventos da conversa para essa sessão.
        response = client.list_events(
            memoryId=MEMORY_ID,
            sessionId=session_id,
            actorId=user_id,
            includePayloads=True,
        )

        raw_events = response.get("events", [])

        # Ordena os eventos por data e hora (os mais antigos primeiro para manter a ordem da conversa)
        raw_events.sort(key=lambda e: e.get("eventId", ""))

        # Limpa e formata os eventos em um formato mais fácil de ler
        messages = []
        for evt in raw_events:
            payloads = evt.get("payload", [])
            for payload in payloads:
                conv = payload.get("conversational", {})
                text = conv.get("content", {}).get("text", "")
                if not text:
                    continue

                try:
                    parsed = json.loads(text)
                except (json.JSONDecodeError, TypeError):
                    continue

                msg = parsed.get("message", {})
                role = msg.get("role")
                content_blocks = msg.get("content", [])

                if role not in ("user", "assistant"):
                    continue

                # Ignora mensagens técnicas de ferramentas — mostra apenas o texto real da conversa
                text_content = extract_text_from_content(content_blocks)
                if not text_content.strip():
                    continue

                messages.append({
                    "role": role,
                    "content": text_content.strip(),
                })

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
            "body": json.dumps(messages),
        }

    except Exception as e:
        print(f"Error getting history for session {session_id}, user {user_id}: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "error": "Failed to retrieve conversation history",
                "message": str(e),
            }),
        }
