#!/usr/bin/env python3
"""CDK app entry point for Earthborne Rangers serverless infrastructure.

Deploy to a specific account/region:
    cdk deploy --all \
        --context account=123456789012 \
        --context region=us-east-1

Stacks:
    EarthborneDb   — VPC + Aurora Serverless v2 (deploy first; RETAIN policy)
    EarthborneApp  — Lambda + API Gateway + S3 + CloudFront
"""
import aws_cdk as cdk

from stacks.database_stack import DatabaseStack
from stacks.app_stack import AppStack

app = cdk.App()

env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1",
)

db_stack = DatabaseStack(app, "EarthborneDb", env=env)

app_stack = AppStack(app, "EarthborneApp", db_stack=db_stack, env=env)
app_stack.add_dependency(db_stack)

app.synth()
