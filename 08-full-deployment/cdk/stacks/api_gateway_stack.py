"""
ApiGatewayStack - REST API layer for Aria (Workshop Module 08).

Creates:
  - REST API Gateway with Cognito authorizer (using existing user pool)
  - DynamoDB table for session metadata (titles, soft-delete)
  - POST   /chat     -> HTTP proxy to AgentCore Runtime (streaming)
  - GET    /sessions -> Lambda: list sessions from DynamoDB
  - PUT    /sessions/{sessionId} -> Lambda: create/update session
  - DELETE /sessions/{sessionId} -> Lambda: soft-delete session
  - GET    /history/{sessionId}  -> Lambda: conversation history from Memory
  - CORS on all endpoints

Exports:
  - api_url: The REST API invoke URL (used by FrontendStack)
"""

import os

import aws_cdk as cdk
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_logs as logs,
    CfnOutput,
    Stack,
)
from constructs import Construct


class ApiGatewayStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ----- Context variables (populated by deploy_frontend.py) -----
        runtime_id = self.node.try_get_context("runtime_id") or "PLACEHOLDER"
        account_id = self.node.try_get_context("account_id") or self.account
        memory_id = self.node.try_get_context("memory_id") or "PLACEHOLDER"
        user_pool_id = self.node.try_get_context("user_pool_id") or "PLACEHOLDER"

        # AgentCore Runtime /invocations endpoint (supports JWT + streaming)
        runtime_url = (
            f"https://bedrock-agentcore.{self.region}.amazonaws.com"
            f"/runtimes/{runtime_id}/invocations"
            f"?qualifier=DEFAULT&accountId={account_id}"
        )

        # ----- Look up existing Cognito User Pool -----
        user_pool = cognito.UserPool.from_user_pool_id(
            self, "ExistingUserPool", user_pool_id
        )

        # ----- REST API -----
        api = apigateway.RestApi(
            self,
            "AriaApi",
            rest_api_name="aria-api",
            description="Aria AI assistant API (streaming proxy + session management)",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
                logging_level=apigateway.MethodLoggingLevel.INFO,
                metrics_enabled=True,
            ),
            endpoint_configuration=apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.REGIONAL],
            ),
        )

        # ----- CORS -----
        cors_options = apigateway.CorsOptions(
            allow_origins=apigateway.Cors.ALL_ORIGINS,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=[
                "Content-Type",
                "Authorization",
                "X-Amz-Date",
                "X-Api-Key",
                "X-Amz-Security-Token",
            ],
            max_age=cdk.Duration.hours(1),
        )

        # ----- Cognito Authorizer -----
        authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self,
            "AriaAuthorizer",
            authorizer_name="aria-cognito-authorizer",
            cognito_user_pools=[user_pool],
            results_cache_ttl=cdk.Duration.minutes(5),
        )

        # ----- IAM Role for API Gateway to invoke Runtime -----
        apigw_runtime_role = iam.Role(
            self,
            "ApiGwRuntimeRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            description="Allows API Gateway to invoke AgentCore Runtime",
        )
        apigw_runtime_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeAgent",
                    "bedrock:Invoke*",
                    "bedrock-agentcore:*",
                ],
                resources=["*"],
            )
        )

        # =====================================================================
        # POST /chat -- Streaming proxy to AgentCore Runtime
        # =====================================================================
        chat_resource = api.root.add_resource("chat")
        chat_resource.add_cors_preflight(**{
            "allow_origins": cors_options.allow_origins,
            "allow_methods": ["POST", "OPTIONS"],
            "allow_headers": cors_options.allow_headers,
        })

        runtime_integration = apigateway.HttpIntegration(
            url=runtime_url,
            http_method="POST",
            proxy=True,
            options=apigateway.IntegrationOptions(
                connection_type=apigateway.ConnectionType.INTERNET,
                timeout=cdk.Duration.seconds(900),
                request_parameters={
                    "integration.request.header.Content-Type": "'application/json'",
                    "integration.request.header.Authorization": "method.request.header.Authorization",
                },
            ),
        )

        post_method = chat_resource.add_method(
            "POST",
            runtime_integration,
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            request_parameters={
                "method.request.header.Authorization": True,
            },
        )

        # Enable streaming via CloudFormation escape hatch
        cfn_method = post_method.node.default_child
        cfn_method.add_property_override(
            "Integration.ResponseTransferMode", "STREAM"
        )

        # =====================================================================
        # DynamoDB table for session metadata
        # =====================================================================
        sessions_table = dynamodb.Table(
            self,
            "AriaSessionsTable",
            table_name="aria-sessions",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="sessionId",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # =====================================================================
        # GET /sessions
        # =====================================================================
        sessions_lambda_path = os.path.join(
            os.path.dirname(__file__), "..", "lambda", "sessions"
        )

        sessions_fn = _lambda.Function(
            self,
            "SessionsFunction",
            function_name="aria-sessions",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="sessions_handler.handler",
            code=_lambda.Code.from_asset(sessions_lambda_path),
            timeout=cdk.Duration.seconds(30),
            memory_size=256,
            environment={
                "SESSIONS_TABLE_NAME": sessions_table.table_name,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        sessions_table.grant_read_data(sessions_fn)

        sessions_resource = api.root.add_resource("sessions")
        sessions_resource.add_cors_preflight(**{
            "allow_origins": cors_options.allow_origins,
            "allow_methods": ["GET", "OPTIONS"],
            "allow_headers": cors_options.allow_headers,
        })

        sessions_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(sessions_fn, proxy=True),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        # PUT /sessions/{sessionId}
        upsert_session_lambda_path = os.path.join(
            os.path.dirname(__file__), "..", "lambda", "upsert_session"
        )

        upsert_session_fn = _lambda.Function(
            self,
            "UpsertSessionFunction",
            function_name="aria-upsert-session",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="upsert_session_handler.handler",
            code=_lambda.Code.from_asset(upsert_session_lambda_path),
            timeout=cdk.Duration.seconds(10),
            memory_size=256,
            environment={
                "SESSIONS_TABLE_NAME": sessions_table.table_name,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        sessions_table.grant_write_data(upsert_session_fn)

        # DELETE /sessions/{sessionId}
        delete_session_lambda_path = os.path.join(
            os.path.dirname(__file__), "..", "lambda", "delete_session"
        )

        delete_session_fn = _lambda.Function(
            self,
            "DeleteSessionFunction",
            function_name="aria-delete-session",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="delete_session_handler.handler",
            code=_lambda.Code.from_asset(delete_session_lambda_path),
            timeout=cdk.Duration.seconds(10),
            memory_size=256,
            environment={
                "SESSIONS_TABLE_NAME": sessions_table.table_name,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        sessions_table.grant_write_data(delete_session_fn)

        session_id_under_sessions = sessions_resource.add_resource("{sessionId}")
        session_id_under_sessions.add_cors_preflight(**{
            "allow_origins": cors_options.allow_origins,
            "allow_methods": ["PUT", "DELETE", "OPTIONS"],
            "allow_headers": cors_options.allow_headers,
        })

        session_id_under_sessions.add_method(
            "PUT",
            apigateway.LambdaIntegration(upsert_session_fn, proxy=True),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        session_id_under_sessions.add_method(
            "DELETE",
            apigateway.LambdaIntegration(delete_session_fn, proxy=True),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        # =====================================================================
        # GET /history/{sessionId}
        # =====================================================================
        history_lambda_path = os.path.join(
            os.path.dirname(__file__), "..", "lambda", "history"
        )

        history_fn = _lambda.Function(
            self,
            "HistoryFunction",
            function_name="aria-history",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="history_handler.handler",
            code=_lambda.Code.from_asset(history_lambda_path),
            timeout=cdk.Duration.seconds(30),
            memory_size=256,
            environment={
                "MEMORY_ID": memory_id,
                "AWS_ACCOUNT_ID": account_id,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        history_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock-agentcore:ListEvents",
                    "bedrock-agentcore:ListMemoryRecords",
                    "bedrock-agentcore:RetrieveMemoryRecords",
                    "bedrock-agentcore:GetMemoryRecord",
                ],
                resources=["*"],
            )
        )

        history_resource = api.root.add_resource("history")
        session_id_resource = history_resource.add_resource("{sessionId}")

        session_id_resource.add_cors_preflight(**{
            "allow_origins": cors_options.allow_origins,
            "allow_methods": ["GET", "OPTIONS"],
            "allow_headers": cors_options.allow_headers,
        })

        session_id_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(history_fn, proxy=True),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        # ----- Workshop cleanup: ensure all resources are deletable -----
        # CDK defaults the API Gateway Account and its CloudWatch role to Retain.
        # Override to Delete so the workshop stack tears down cleanly.
        for child in api.node.find_all():
            if isinstance(child, cdk.CfnResource):
                if child.cfn_resource_type in (
                    "AWS::ApiGateway::Account",
                    "AWS::IAM::Role",
                ):
                    child.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # ----- Exports -----
        self.api_url = api.url

        CfnOutput(self, "ApiUrl", value=api.url, description="Aria API URL")
        CfnOutput(
            self,
            "RuntimeIntegrationUrl",
            value=runtime_url,
            description="AgentCore Runtime URL for /chat endpoint",
        )
