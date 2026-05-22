"""Deploy the Aria frontend web application.

Reads workshop configs and CloudFormation outputs, then:
  1. Configures the Runtime for OAuth (CUSTOM_JWT)
  2. Adds POST /chat endpoint to the pre-provisioned API Gateway
  3. Updates the history Lambda with the Memory ID
  4. Uploads frontend files + generated config.js to S3
  5. Invalidates the CloudFront cache

The API Gateway, Lambda functions, S3 bucket, CloudFront distribution, and
DynamoDB sessions table are all pre-provisioned by the workshop CloudFormation
template — this script just wires them up with the runtime-specific values
that aren't known until modules 02-07 have been completed.

Run from notebook or command line:
    python deploy_frontend.py
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import boto3
from botocore.exceptions import ClientError
from shared import utils


def deploy():
    """Main deployment function."""
    region = utils.get_region()
    account_id = utils.get_account_id()

    utils.print_banner("Frontend Deployment")
    print(f"  Region:  {region}")
    print(f"  Account: {account_id}")
    print()

    # --- Gather configuration ---
    print("[1/5] Gathering configuration...")

    cfn = utils.get_all_cfn_outputs()
    user_pool_id = cfn.get("UserPoolId")
    client_id = cfn.get("UserPoolClientId")
    cognito_domain_url = cfn.get("CognitoDomainUrl", "")
    frontend_api_id = cfn.get("FrontendApiId")
    chat_resource_id = cfn.get("FrontendChatResourceId")
    cloudfront_url = cfn.get("CloudFrontUrl")
    cloudfront_dist_id = cfn.get("CloudFrontDistributionId")
    frontend_bucket = cfn.get("FrontendBucketName")
    api_url = cfn.get("FrontendApiUrl")

    if not all([user_pool_id, client_id, frontend_api_id, chat_resource_id]):
        raise RuntimeError(
            "Required CloudFormation outputs not found. "
            "Ensure the workshop CFN stack is deployed."
        )

    cognito_domain = cognito_domain_url.replace("https://", "").split(".")[0]

    runtime_config = utils.load_config("runtime")
    if not runtime_config:
        raise RuntimeError("Runtime config not found. Run Module 02 first.")
    runtime_id = runtime_config["runtime_id"]

    memory_config = utils.load_config("memory")
    memory_id = memory_config["memory_id"] if memory_config else ""

    print(f"  Runtime ID:     {runtime_id}")
    print(f"  Memory ID:      {memory_id or '(not configured)'}")
    print(f"  API Gateway:    {frontend_api_id}")
    print(f"  CloudFront:     {cloudfront_url}")

    control = boto3.client("bedrock-agentcore-control", region_name=region)
    apigw = boto3.client("apigateway", region_name=region)
    s3 = boto3.client("s3", region_name=region)
    lam = boto3.client("lambda", region_name=region)
    cf = boto3.client("cloudfront", region_name=region)

    # --- Configure Runtime OAuth ---
    print()
    print("[2/5] Configuring Runtime for OAuth (CUSTOM_JWT)...")

    discovery_url = (
        f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
        f"/.well-known/openid-configuration"
    )

    rt = control.get_agent_runtime(agentRuntimeId=runtime_id)
    existing_auth = rt.get("authorizerConfiguration", {})

    if existing_auth.get("customJWTAuthorizer", {}).get("discoveryUrl") == discovery_url:
        print("  Runtime already configured for OAuth")
    else:
        update_params = {
            "agentRuntimeId": runtime_id,
            "roleArn": rt["roleArn"],
            "agentRuntimeArtifact": rt["agentRuntimeArtifact"],
            "networkConfiguration": rt["networkConfiguration"],
            "authorizerConfiguration": {
                "customJWTAuthorizer": {
                    "discoveryUrl": discovery_url,
                    "allowedAudience": [client_id],
                }
            },
            "requestHeaderConfiguration": {
                "requestHeaderAllowlist": ["Authorization"],
            },
        }
        if rt.get("environmentVariables"):
            update_params["environmentVariables"] = rt["environmentVariables"]
        if rt.get("lifecycleConfiguration"):
            update_params["lifecycleConfiguration"] = rt["lifecycleConfiguration"]

        control.update_agent_runtime(**update_params)
        print(f"  Discovery URL: {discovery_url}")

        utils.poll_until(
            describe_fn=lambda: control.get_agent_runtime(agentRuntimeId=runtime_id),
            target_statuses={"READY"},
            label="Runtime (OAuth update)",
            timeout=120,
        )

    # --- Add POST /chat endpoint ---
    print()
    print("[3/5] Configuring /chat endpoint...")

    runtime_url = (
        f"https://bedrock-agentcore.{region}.amazonaws.com"
        f"/runtimes/{runtime_id}/invocations"
        f"?qualifier=DEFAULT&accountId={account_id}"
    )

    # Ensure POST method exists on /chat (idempotent)
    method_exists = False
    try:
        apigw.get_method(
            restApiId=frontend_api_id,
            resourceId=chat_resource_id,
            httpMethod="POST",
        )
        method_exists = True
    except ClientError as e:
        if "NotFoundException" not in str(e):
            raise

    if not method_exists:
        print("  Creating POST /chat method...")
        apigw.put_method(
            restApiId=frontend_api_id,
            resourceId=chat_resource_id,
            httpMethod="POST",
            authorizationType="COGNITO_USER_POOLS",
            authorizerId=_get_authorizer_id(apigw, frontend_api_id),
            requestParameters={
                "method.request.header.Authorization": True,
            },
        )

    # Ensure integration exists and points to the current runtime (idempotent)
    integration_params = dict(
        restApiId=frontend_api_id,
        resourceId=chat_resource_id,
        httpMethod="POST",
        type="HTTP_PROXY",
        integrationHttpMethod="POST",
        uri=runtime_url,
        connectionType="INTERNET",
        timeoutInMillis=29000,
        requestParameters={
            "integration.request.header.Content-Type": "'application/json'",
            "integration.request.header.Authorization": "method.request.header.Authorization",
        },
    )

    try:
        apigw.get_integration(
            restApiId=frontend_api_id,
            resourceId=chat_resource_id,
            httpMethod="POST",
        )
        print("  POST /chat integration exists, updating URI...")
        apigw.update_integration(
            restApiId=frontend_api_id,
            resourceId=chat_resource_id,
            httpMethod="POST",
            patchOperations=[
                {"op": "replace", "path": "/uri", "value": runtime_url},
            ],
        )
    except ClientError as e:
        if "NotFoundException" not in str(e):
            raise
        print("  Creating POST /chat integration...")
        apigw.put_integration(**integration_params)

    # Enable streaming: ResponseTransferMode=STREAM ensures API Gateway
    # forwards response chunks as the agent yields them instead of buffering
    # the entire response (which would hit the 29s integration timeout).
    apigw.update_integration(
        restApiId=frontend_api_id,
        resourceId=chat_resource_id,
        httpMethod="POST",
        patchOperations=[
            {"op": "replace", "path": "/responseTransferMode", "value": "STREAM"},
        ],
    )
    print("  Streaming mode enabled (ResponseTransferMode=STREAM)")

    # Create a new deployment to make changes live
    print("  Deploying API Gateway...")
    apigw.create_deployment(
        restApiId=frontend_api_id,
        stageName="prod",
        description="Frontend deployment with /chat endpoint",
    )
    print("  API Gateway deployed")

    # --- Update history Lambda with Memory ID ---
    if memory_id:
        print()
        print("  Updating history Lambda with Memory ID...")
        try:
            lam.update_function_configuration(
                FunctionName="aria-history",
                Environment={"Variables": {"MEMORY_ID": memory_id}},
            )
            print(f"  History Lambda updated (MEMORY_ID={memory_id})")
        except ClientError as e:
            print(f"  Warning: Could not update history Lambda: {e}")

    # --- Upload frontend files + config.js ---
    print()
    print("[4/5] Deploying frontend files to S3...")

    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

    cognito_domain_full = (
        f"https://{cognito_domain}.auth.{region}.amazoncognito.com"
    )

    config_js = f"""\
// Auto-generated by deploy_frontend.py. Do not edit manually.
window.ARIA_CONFIG = {{
    API_URL: "{api_url}",
    RUNTIME_URL: "{runtime_url}",
    COGNITO_DOMAIN: "{cognito_domain_full}",
    USER_POOL_ID: "{user_pool_id}",
    CLIENT_ID: "{client_id}",
    REDIRECT_URI: "{cloudfront_url}/callback",
    LOGOUT_URI: "{cloudfront_url}/",
    REGION: "{region}"
}};
"""

    # Upload frontend files
    content_types = {
        ".html": "text/html",
        ".js": "application/javascript",
        ".css": "text/css",
        ".json": "application/json",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
    }

    uploaded = 0
    for root, _, files in os.walk(frontend_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            key = os.path.relpath(filepath, frontend_dir)
            ext = os.path.splitext(filename)[1].lower()
            ct = content_types.get(ext, "application/octet-stream")

            with open(filepath, "rb") as f:
                s3.put_object(
                    Bucket=frontend_bucket,
                    Key=key,
                    Body=f.read(),
                    ContentType=ct,
                )
            uploaded += 1

    # Upload generated config.js
    s3.put_object(
        Bucket=frontend_bucket,
        Key="config.js",
        Body=config_js.encode(),
        ContentType="application/javascript",
    )
    uploaded += 1

    print(f"  Uploaded {uploaded} files to s3://{frontend_bucket}")

    # --- Invalidate CloudFront ---
    print()
    print("[5/5] Invalidating CloudFront cache...")

    try:
        cf.create_invalidation(
            DistributionId=cloudfront_dist_id,
            InvalidationBatch={
                "Paths": {"Quantity": 1, "Items": ["/*"]},
                "CallerReference": str(int(time.time())),
            },
        )
        print("  Cache invalidation started")
    except ClientError as e:
        print(f"  ⚠ Cache invalidation skipped (permission not available): {e.response['Error']['Code']}")
        print("  Files are uploaded — CloudFront will serve them after its default TTL expires.")

    # --- Save config ---
    config = {
        "cloudfront_url": cloudfront_url,
        "api_url": api_url,
        "user_pool_id": user_pool_id,
        "client_id": client_id,
        "cognito_domain": cognito_domain,
        "runtime_id": runtime_id,
        "memory_id": memory_id,
        "region": region,
    }
    utils.save_config("frontend", config)

    # --- Print results ---
    print()
    utils.print_banner("Deployment Complete")
    print(f"  Frontend URL:  {cloudfront_url}")
    print(f"  API URL:       {api_url}")
    print()
    print("  Login credentials:")
    print("    Username: workshop@example.com")
    print("    Password: WorkshopPass123!")
    print()
    print(f"  Open {cloudfront_url} in your browser to use Aria.")
    print()

    return config


def _get_authorizer_id(apigw, api_id: str) -> str:
    """Find the Cognito authorizer ID on the API Gateway."""
    resp = apigw.get_authorizers(restApiId=api_id)
    for auth in resp.get("items", []):
        if auth.get("type") == "COGNITO_USER_POOLS":
            return auth["id"]
    raise RuntimeError("No Cognito authorizer found on the API Gateway")


if __name__ == "__main__":
    deploy()
