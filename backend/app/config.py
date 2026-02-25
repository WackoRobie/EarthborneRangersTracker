from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://rangers:rangers@localhost:5432/earthborne"
    cors_origins: list[str] = ["http://localhost:3000"]
    jwt_secret: str = "change-me-in-production"
    token_expire_days: int = 30
    registration_token: str | None = None  # None = registration disabled

    class Config:
        env_file = ".env"


settings = Settings()
