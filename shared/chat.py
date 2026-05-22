#!/usr/bin/env python3
"""Interactive CLI chat client for the Aria agent.

Talks directly to a deployed AgentCore Runtime agent with streaming output.
Supports both IAM (SigV4) and OAuth (JWT) authentication modes.

Usage from any module directory:
    python ../shared/chat.py              # IAM auth (Modules 02-04)
    python ../shared/chat.py --auth       # OAuth/JWT auth (Modules 05+)
"""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared import utils

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_DIR = Path(__file__).resolve().parent / ".config"


def _load_config(name: str) -> dict | None:
    path = CONFIG_DIR / f"{name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def _get_region() -> str:
    return os.environ.get("AWS_REGION", "us-east-1")


def _get_cfn_outputs() -> dict:
    cfn = boto3.client("cloudformation", region_name=_get_region())
    try:
        resp = cfn.describe_stacks(StackName="cfn-template")
        outputs = resp["Stacks"][0].get("Outputs", [])
        return {o["OutputKey"]: o["OutputValue"] for o in outputs}
    except ClientError:
        return {}


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def _get_jwt_token() -> str:
    """Authenticate the workshop test user and return a JWT ID token."""
    region = _get_region()
    cfn = _get_cfn_outputs()

    user_pool_id = cfn.get("UserPoolId") or cfn.get("CognitoUserPoolId")
    client_id = cfn.get("UserPoolClientId") or cfn.get("CognitoClientId")

    if not user_pool_id or not client_id:
        print("Error: Could not find Cognito details in CloudFormation outputs.")
        sys.exit(1)

    cognito = boto3.client("cognito-idp", region_name=region)

    username = "workshop@example.com"
    password = "WorkshopPass123!"

    # Ensure test user exists
    try:
        cognito.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[
                {"Name": "email", "Value": username},
                {"Name": "email_verified", "Value": "true"},
            ],
            MessageAction="SUPPRESS",
        )
        cognito.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=password,
            Permanent=True,
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "UsernameExistsException":
            raise

    resp = cognito.initiate_auth(
        ClientId=client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
    )

    return resp["AuthenticationResult"]["IdToken"]


# ---------------------------------------------------------------------------
# Agent invocation (streaming)
# ---------------------------------------------------------------------------


def invoke_streaming(
    runtime_arn: str,
    session_id: str,
    prompt: str,
    jwt_token: str | None = None,
    region: str = "us-east-1",
) -> str:
    """Invoke the agent and stream the response to stdout. Returns full text."""
    client = boto3.client("bedrock-agentcore", region_name=region)

    payload = {"prompt": prompt, "session_id": session_id}
    if jwt_token:
        payload["authorization"] = f"Bearer {jwt_token}"

    response = client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(payload).encode(),
    )

    return utils.stream_sse_response(response["response"])


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Chat with the Aria agent")
    parser.add_argument(
        "--auth",
        action="store_true",
        help="Use OAuth/JWT authentication (required from Module 05 onwards)",
    )
    args = parser.parse_args()

    # Load runtime config
    runtime_config = _load_config("runtime")
    if not runtime_config:
        print("Error: No runtime config found. Deploy the agent first (Module 02).")
        sys.exit(1)

    runtime_arn = runtime_config["runtime_arn"]
    region = _get_region()
    session_id = str(uuid.uuid4())

    # Authenticate if needed
    jwt_token = None
    if args.auth:
        print("Authenticating...")
        jwt_token = _get_jwt_token()
        auth_label = "OAuth (JWT)"
    else:
        auth_label = "IAM (direct)"

    print()
    print("=" * 50)
    print("  Aria - AgentCore Workshop")
    print("=" * 50)
    print(f"  Auth:    {auth_label}")
    print(f"  Session: {session_id[:8]}...")
    print()
    print("  Commands: 'quit' to exit, 'new' for new session")
    print("=" * 50)

    while True:
        try:
            prompt = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not prompt:
            continue
        if prompt.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        if prompt.lower() == "new":
            session_id = str(uuid.uuid4())
            print(f"New session: {session_id[:8]}...")
            continue

        print("\nAria: ", end="", flush=True)
        try:
            invoke_streaming(runtime_arn, session_id, prompt, jwt_token, region)
        except ClientError as e:
            print(f"\nError: {e}")
        except Exception as e:
            print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()
