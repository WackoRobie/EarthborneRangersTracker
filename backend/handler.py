"""AWS Lambda entry point.

Mangum wraps the FastAPI ASGI app so API Gateway can invoke it.
lifespan="off" because Lambda does not support ASGI lifespan events —
schema migrations and seeding are handled as separate deploy-time steps.

resolve() must be called before importing app.main so that
pydantic-settings reads the correct DATABASE_URL / JWT_SECRET env vars
when Settings() is first instantiated.
"""
from app.lambda_secrets import resolve

resolve()  # populate env vars before Settings() is instantiated

from mangum import Mangum  # noqa: E402

from app.main import app  # noqa: E402

handler = Mangum(app, lifespan="off")
