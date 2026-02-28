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
    """Run ``alembic upgrade head`` then seed reference data.

    Pass ``{"stamp_base": true}`` in the event payload to first reset the
    alembic_version table to base before upgrading.  Use this once when
    recovering from a broken/empty initial migration.
    """
    resolve()  # populate DATABASE_URL before alembic reads config

    # Import alembic here so the cold-start resolve() runs first.
    from alembic import command as alembic_command
    from alembic.config import Config

    cfg = Config("alembic.ini")
    if event.get("stamp_base"):
        # Use raw SQL to clear alembic_version when the old revision file no
        # longer exists and alembic stamp can't resolve it.
        import sqlalchemy as sa
        from app.config import settings
        engine = sa.create_engine(settings.database_url)
        with engine.connect() as conn:
            conn.execute(sa.text("DELETE FROM alembic_version"))
            conn.commit()
        log.info("Cleared alembic_version table")

    log.info("Running alembic upgrade head")
    alembic_command.upgrade(cfg, "head")
    log.info("Migrations complete")

    # Seed reference data (cards + storylines) — idempotent, safe to re-run.
    from app.database import SessionLocal
    from app.seed import seed_reference_data
    db = SessionLocal()
    try:
        seed_reference_data(db)
        log.info("Reference data seeded")
    finally:
        db.close()

    return {"status": "ok"}
