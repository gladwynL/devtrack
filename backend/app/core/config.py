from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration, populated from environment variables."""

    # DevTrack keeps a single .env at the repository root (see .env.example there).
    # Both paths are checked so this works whether uvicorn/pytest is run from
    # the repo root or from backend/.
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DevTrack API"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg2://devtrack:devtrack@localhost:5432/devtrack"

    cors_origins: list[str] = ["http://localhost:5173"]

    # Insecure by design: a working default so local dev/tests don't require
    # a .env file. Every real deployment must override this via environment
    # variables (see .env.example).
    jwt_secret_key: str = "insecure-dev-secret-change-me-before-deploying-anywhere-real"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
