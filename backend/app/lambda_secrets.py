"""Resolve AWS Secrets Manager secrets at Lambda cold start.

Call resolve() exactly once, before any module that imports app.config
is loaded, so that pydantic-settings picks up the env vars when
Settings() is first instantiated.

Outside Lambda (LAMBDA_ENV unset) this is a no-op — local dev and tests
continue to use .env / docker-compose environment variables.
"""
import json
import os


def resolve() -> None:
    """Fetch DB + app secrets from Secrets Manager and set env vars.

    Reads:
      DB_SECRET_ARN  — Aurora secret JSON: {username, password, host, port, dbname}
      APP_SECRET_ARN — App secret JSON:    {JWT_SECRET, REGISTRATION_TOKEN}

    Writes env vars:
      DATABASE_URL, JWT_SECRET, REGISTRATION_TOKEN
    """
    if not os.getenv("LAMBDA_ENV"):
        return

    import boto3  # only available in Lambda environment / local AWS profile

    sm = boto3.client("secretsmanager")

    # ── Database secret ────────────────────────────────────────────────────
    db_secret_arn = os.environ["DB_SECRET_ARN"]
    db = json.loads(sm.get_secret_value(SecretId=db_secret_arn)["SecretString"])
    os.environ["DATABASE_URL"] = (
        f"postgresql://{db['username']}:{db['password']}"
        f"@{db['host']}:{db['port']}/{db['dbname']}"
    )

    # ── Application secret ─────────────────────────────────────────────────
    app_secret_arn = os.environ["APP_SECRET_ARN"]
    app = json.loads(sm.get_secret_value(SecretId=app_secret_arn)["SecretString"])
    os.environ["JWT_SECRET"] = app["JWT_SECRET"]
    if reg_token := app.get("REGISTRATION_TOKEN"):
        os.environ["REGISTRATION_TOKEN"] = reg_token
