"""
Lambda handler for PUT /sessions/{sessionId}.

Creates or updates a session record in DynamoDB. This is called by the
frontend when the user sends the first message in a conversation.

The upsert is idempotent: the first call sets title and createdAt,
subsequent calls only update updatedAt.
"""

import json
import os
from datetime import datetime, timezone

import boto3

SESSIONS_TABLE_NAME = os.environ.get("SESSIONS_TABLE_NAME", "aria-sessions")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(SESSIONS_TABLE_NAME)


def get_user_id(event: dict) -> str:
    """Extract the user ID (sub) from the Cognito JWT claims."""
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    return claims.get("sub", "unknown")


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
        body = json.loads(event.get("body") or "{}")
    except (json.JSONDecodeError, TypeError):
        body = {}

    title = body.get("title", "New conversation")

    try:
        now = datetime.now(timezone.utc).isoformat()

        table.update_item(
            Key={"userId": user_id, "sessionId": session_id},
            UpdateExpression=(
                "SET title = if_not_exists(title, :title), "
                "createdAt = if_not_exists(createdAt, :now), "
                "updatedAt = :now, "
                "deleted = if_not_exists(deleted, :false)"
            ),
            ExpressionAttributeValues={
                ":title": title,
                ":now": now,
                ":false": False,
            },
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
            "body": json.dumps({
                "sessionId": session_id,
                "title": title,
            }),
        }

    except Exception as e:
        print(f"Error upserting session {session_id} for user {user_id}: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "error": "Failed to create/update session",
                "message": str(e),
            }),
        }
