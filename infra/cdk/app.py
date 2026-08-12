#!/usr/bin/env python3
"""
CDK application for the Aria frontend deployment (Workshop Module 08).

Deploys two stacks:
  1. AriaApiGatewayStack  - REST API with Cognito auth, streaming proxy to Runtime,
                            session management endpoints (DynamoDB + Lambda)
  2. AriaFrontendStack    - S3 + CloudFront + generated config.js

Uses the existing Cognito User Pool created by the workshop CloudFormation template.
Context variables (populated by deploy_frontend.py):
  - user_pool_id, client_id, cognito_domain, runtime_id, memory_id, account_id
"""

import aws_cdk as cdk

from stacks.api_gateway_stack import ApiGatewayStack
from stacks.frontend_stack import FrontendStack

app = cdk.App()

region = app.node.try_get_context("region") or "us-east-1"
env = cdk.Environment(region=region)

api_gw = ApiGatewayStack(app, "AriaApiGatewayStack", env=env)

frontend = FrontendStack(
    app,
    "AriaFrontendStack",
    api_url=api_gw.api_url,
    env=env,
)

app.synth()
