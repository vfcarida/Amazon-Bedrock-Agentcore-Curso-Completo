"""Test harness for invoking a deployed AgentCore Runtime agent.

Provides invoke() and stream() functions for use in notebook cells.
Handles both authenticated (JWT) and unauthenticated invocations.
"""

import json
import uuid

import boto3
from botocore.exceptions import ClientError

from . import utils


def invoke(
    prompt: str,
    session_id: str | None = None,
    jwt_token: str | None = None,
    runtime_arn: str | None = None,
    print_response: bool = True,
) -> dict:
    """Invoke the deployed agent and return the response.

    Args:
        prompt: The user message to send.
        session_id: Session ID for conversation continuity. Auto-generated if None.
        jwt_token: Optional JWT for authenticated invocations.
        runtime_arn: Runtime ARN. Auto-loaded from saved config if None.
        print_response: Whether to print the response text.

    Returns:
        Dict with response_text, session_id, and raw response metadata.
    """
    region = utils.get_region()
    config = utils.load_config("runtime")

    if runtime_arn is None:
        if config:
            runtime_arn = config["runtime_arn"]
        else:
            raise ValueError(
                "runtime_arn not provided and no saved config found. "
                "Deploy the agent first using deploy_agent.deploy()."
            )

    session_id = session_id or str(uuid.uuid4())

    payload = json.dumps({"prompt": prompt, "session_id": session_id}).encode()

    client = boto3.client("bedrock-agentcore", region_name=region)

    # If JWT provided, include it in the payload for the agent to forward to Gateway
    if jwt_token:
        payload_dict = json.loads(payload.decode())
        payload_dict["authorization"] = f"Bearer {jwt_token}"
        payload = json.dumps(payload_dict).encode()

    invoke_params = {
        "agentRuntimeArn": runtime_arn,
        "runtimeSessionId": session_id,
        "payload": payload,
    }

    print(f"🤖 Sending: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    print(f"   Session: {session_id[:16]}...")
    print()

    try:
        response = client.invoke_agent_runtime(**invoke_params)
    except ClientError as e:
        print(f"❌ Invocation failed: {e}")
        raise

    # Stream the SSE response, printing text as it arrives
    if print_response:
        print("💬 Response:")
        print("-" * 40)
        response_text = utils.stream_sse_response(response["response"])
        print("-" * 40)
    else:
        raw = response["response"].read().decode("utf-8")
        response_text = utils.parse_sse_text(raw)

    return {
        "response_text": response_text,
        "session_id": session_id,
        "runtime_arn": runtime_arn,
    }


def get_test_token(
    user_pool_id: str | None = None,
    client_id: str | None = None,
    username: str = "workshop@example.com",
    password: str = "WorkshopPass123!",
) -> str:
    """Authenticate a test user and return the ID token.

    Auto-discovers Cognito details from CFN outputs if not provided.

    Returns:
        The JWT ID token string.
    """
    cfn = utils.get_all_cfn_outputs()

    if user_pool_id is None:
        user_pool_id = cfn.get("UserPoolId") or cfn.get("CognitoUserPoolId")
    if client_id is None:
        client_id = cfn.get("UserPoolClientId") or cfn.get("CognitoClientId")

    if not user_pool_id or not client_id:
        raise ValueError("Could not discover Cognito details from CFN outputs.")

    region = utils.get_region()
    cognito = boto3.client("cognito-idp", region_name=region)

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
        print(f"✅ Test user created: {username}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "UsernameExistsException":
            print(f"✅ Test user already exists: {username}")
        else:
            raise

    # Authenticate
    resp = cognito.initiate_auth(
        ClientId=client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
    )

    token = resp["AuthenticationResult"]["IdToken"]
    print(f"🔑 Token obtained ({len(token)} chars, valid for 1 hour)")
    return token
