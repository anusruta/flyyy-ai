from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # PostgreSQL in Docker; falls back to SQLite for local dev without Docker
    DATABASE_URL: str = "postgresql+asyncpg://flyy:flyy_secret@localhost:5432/flyy_db"
    SYNC_DATABASE_URL: str = "postgresql://flyy:flyy_secret@localhost:5432/flyy_db"

    OTEL_SERVICE_NAME: str = "flyy-backend"
    RETENTION_CHECK_INTERVAL_HOURS: int = 1

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
