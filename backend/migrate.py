"""Alembic migration Lambda handler.

Invoke this function once after deploying a new AppStack version to apply
pending database migrations:

    aws lambda invoke \\
        --function-name <MigrateFunctionName> \\
        --payload '{}' \\
        /dev/stdout

The function name is printed as a CDK output (MigrateFunctionName).
"""
import logging

from app.lambda_secrets import resolve

log = logging.getLogger(__name__)


def handler(event, context):
    """Run ``alembic upgrade head`` against the Aurora cluster."""
    resolve()  # populate DATABASE_URL before alembic reads config

    # Import alembic here so the cold-start resolve() runs first.
    from alembic import command as alembic_command
    from alembic.config import Config

    cfg = Config("alembic.ini")
    log.info("Running alembic upgrade head")
    alembic_command.upgrade(cfg, "head")
    log.info("Migrations complete")
    return {"status": "ok"}
