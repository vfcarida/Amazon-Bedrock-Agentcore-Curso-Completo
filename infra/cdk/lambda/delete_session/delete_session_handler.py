"""
Lambda handler for DELETE /sessions/{sessionId}.

Soft-deletes a conversation session by setting deleted=true in DynamoDB.
The user ID is extracted from the Cognito JWT claims to ensure users can
only delete their own sessions.
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
        now = datetime.now(timezone.utc).isoformat()

        table.update_item(
            Key={"userId": user_id, "sessionId": session_id},
            UpdateExpression="SET deleted = :d, updatedAt = :now",
            ExpressionAttributeValues={":d": True, ":now": now},
        )

        print(f"Soft-deleted session {session_id} for user {user_id}")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
            "body": json.dumps({
                "sessionId": session_id,
                "deleted": True,
            }),
        }

    except Exception as e:
        print(f"Error deleting session {session_id} for user {user_id}: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "error": "Failed to delete session",
                "message": str(e),
            }),
        }
