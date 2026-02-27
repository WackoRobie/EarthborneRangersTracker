"""AWS Lambda entry point.

Mangum wraps the FastAPI ASGI app so API Gateway can invoke it.
lifespan="off" because Lambda does not support ASGI lifespan events —
schema migrations and seeding are handled as separate deploy-time steps.
"""
from mangum import Mangum

from app.main import app

handler = Mangum(app, lifespan="off")
