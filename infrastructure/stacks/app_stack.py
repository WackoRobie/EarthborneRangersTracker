"""AppStack — Lambda + API Gateway (HTTP) + S3 + CloudFront.

Requires DatabaseStack to be deployed first (db_stack parameter carries
the VPC, security group, and DB secret).

Deploy:
    cdk deploy EarthborneApp \\
        --context account=<ACCOUNT_ID> \\
        --context region=us-east-1
"""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct

from stacks.database_stack import DatabaseStack


class AppStack(Stack):
    """Lambda (FastAPI via Mangum) + HTTP API Gateway + S3/CloudFront frontend."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        db_stack: DatabaseStack,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ── App secrets (JWT_SECRET, REGISTRATION_TOKEN) ───────────────────
        app_secret = secretsmanager.Secret(
            self,
            "AppSecret",
            description="Earthborne Rangers — JWT secret and registration token",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"REGISTRATION_TOKEN":"change-me"}',
                generate_string_key="JWT_SECRET",
                exclude_punctuation=True,
                password_length=64,
            ),
        )

        # ── Lambda security group ──────────────────────────────────────────
        lambda_sg = ec2.SecurityGroup(
            self,
            "LambdaSg",
            vpc=db_stack.vpc,
            description="Earthborne Rangers Lambda — egress to Aurora + internet",
            allow_all_outbound=True,
        )
        # Allow the Lambda SG to reach Aurora on 5432
        db_stack.db_security_group.add_ingress_rule(
            peer=lambda_sg,
            connection=ec2.Port.tcp(5432),
            description="Lambda → Aurora",
        )

        # ── Lambda execution role ──────────────────────────────────────────
        lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaVPCAccessExecutionRole"
                ),
            ],
        )
        # Read both secrets
        db_stack.db_secret.grant_read(lambda_role)
        app_secret.grant_read(lambda_role)

        # ── Lambda function ────────────────────────────────────────────────
        # Package the entire backend/ directory as a zip asset.
        # The function handler is handler.handler (backend/handler.py).
        backend_function = lambda_.Function(
            self,
            "ApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=lambda_.Code.from_asset(
                "../backend",
                # Exclude test files, __pycache__, venv artefacts
                exclude=[
                    ".venv",
                    "venv",
                    "__pycache__",
                    "*.pyc",
                    "tests/",
                    "alembic/",
                    "alembic.ini",
                    ".pytest_cache",
                    ".env",
                ],
            ),
            vpc=db_stack.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[lambda_sg],
            environment={
                "LAMBDA_ENV": "1",
                "DB_SECRET_ARN": db_stack.db_secret.secret_arn,
                "APP_SECRET_ARN": app_secret.secret_arn,
            },
            timeout=Duration.seconds(29),  # API GW hard limit is 30 s
            memory_size=512,
            role=lambda_role,
        )

        # ── HTTP API Gateway ───────────────────────────────────────────────
        http_api = apigwv2.HttpApi(
            self,
            "HttpApi",
            api_name="earthborne-rangers",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_origins=["*"],  # CloudFront origin added after deploy
                allow_methods=[
                    apigwv2.CorsHttpMethod.GET,
                    apigwv2.CorsHttpMethod.POST,
                    apigwv2.CorsHttpMethod.PATCH,
                    apigwv2.CorsHttpMethod.DELETE,
                    apigwv2.CorsHttpMethod.OPTIONS,
                ],
                allow_headers=["Authorization", "Content-Type"],
                max_age=Duration.hours(1),
            ),
        )
        http_api.add_routes(
            path="/{proxy+}",
            methods=[apigwv2.HttpMethod.ANY],
            integration=integrations.HttpLambdaIntegration(
                "LambdaIntegration", backend_function
            ),
        )

        # ── S3 bucket for frontend static assets ───────────────────────────
        frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=cdk.RemovalPolicy.RETAIN,
            auto_delete_objects=False,
        )

        # ── CloudFront distribution ────────────────────────────────────────
        oac = cloudfront.S3OriginAccessControl(
            self,
            "OAC",
            description="Earthborne Rangers frontend OAC",
            signing=cloudfront.Signing.SIGV4_NO_OVERRIDE,
        )

        api_origin = origins.HttpOrigin(
            f"{http_api.http_api_id}.execute-api.{self.region}.amazonaws.com",
            protocol_policy=cloudfront.OriginProtocolPolicy.HTTPS_ONLY,
        )

        distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    frontend_bucket, origin_access_control=oac
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            additional_behaviors={
                "/api/*": cloudfront.BehaviorOptions(
                    origin=api_origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
                ),
            },
            default_root_object="index.html",
            error_responses=[
                # SPA fallback — serve index.html for any 403/404 from S3
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
            ],
        )

        # Grant CloudFront read access to the S3 bucket via OAC
        frontend_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[frontend_bucket.arn_for_objects("*")],
                principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
                conditions={
                    "StringEquals": {
                        "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution.distribution_id}"
                    }
                },
            )
        )

        # ── Migrate Lambda (runs Alembic on demand) ────────────────────────
        migrate_function = lambda_.Function(
            self,
            "MigrateFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="migrate.handler",
            code=lambda_.Code.from_asset(
                "../backend",
                exclude=[
                    ".venv",
                    "venv",
                    "__pycache__",
                    "*.pyc",
                    "tests/",
                    ".pytest_cache",
                    ".env",
                ],
            ),
            vpc=db_stack.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[lambda_sg],
            environment={
                "LAMBDA_ENV": "1",
                "DB_SECRET_ARN": db_stack.db_secret.secret_arn,
                "APP_SECRET_ARN": app_secret.secret_arn,
            },
            timeout=Duration.minutes(5),
            memory_size=256,
            role=lambda_role,
        )
        db_stack.db_secret.grant_read(migrate_function.role)  # type: ignore[arg-type]

        # ── Outputs ────────────────────────────────────────────────────────
        cdk.CfnOutput(self, "CloudFrontUrl", value=f"https://{distribution.distribution_domain_name}")
        cdk.CfnOutput(self, "ApiGatewayUrl", value=http_api.url or "")
        cdk.CfnOutput(self, "FrontendBucketName", value=frontend_bucket.bucket_name)
        cdk.CfnOutput(self, "AppSecretArn", value=app_secret.secret_arn)
        cdk.CfnOutput(self, "MigrateFunctionName", value=migrate_function.function_name)
