"""
Lambda handler for GET /sessions.

Lists conversation sessions for the authenticated user from DynamoDB.
The user ID is extracted from the Cognito JWT claims passed through by
API Gateway's Cognito authorizer.
"""

import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key, Attr

SESSIONS_TABLE_NAME = os.environ.get("SESSIONS_TABLE_NAME", "aria-sessions")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(SESSIONS_TABLE_NAME)


def decimal_default(obj):
    """JSON serializer for Decimal types returned by DynamoDB."""
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def get_user_id(event: dict) -> str:
    """Extract the user ID (sub) from the Cognito JWT claims."""
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    return claims.get("sub", "unknown")


def handler(event, context):
    user_id = get_user_id(event)

    try:
        result = table.query(
            KeyConditionExpression=Key("userId").eq(user_id),
            FilterExpression=Attr("deleted").ne(True),
        )

        sessions = sorted(
            result.get("Items", []),
            key=lambda s: s.get("updatedAt", ""),
            reverse=True,
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
            "body": json.dumps({
                "sessions": sessions,
                "userId": user_id,
            }, default=decimal_default),
        }

    except Exception as e:
        print(f"Error listing sessions for user {user_id}: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "error": "Failed to list sessions",
                "message": str(e),
            }),
        }
