import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings

# Lambda execution environments are reused between invocations but DB
# connections can go stale, especially with Aurora Serverless. Use NullPool
# in Lambda so each invocation opens and closes its own connection cleanly.
# Local dev uses the default QueuePool with pre-ping for resilience.
if os.getenv("LAMBDA_ENV"):
    engine = create_engine(settings.database_url, poolclass=NullPool)
else:
    engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a DB session and ensures it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
