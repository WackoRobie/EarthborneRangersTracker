from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://rangers:rangers@localhost:5432/earthborne"
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
