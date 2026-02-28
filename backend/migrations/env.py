from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from alembic import context

# Alembic Config object — access to values in alembic.ini.
config = context.config

# Set up loggers from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so autogenerate can diff against the full schema.
import app.models  # noqa: F401
from app.config import settings
from app.database import Base

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit migration SQL to stdout without a live DB connection."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live DB connection."""
    connectable = create_engine(settings.database_url, poolclass=NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
