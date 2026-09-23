from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULT_JWT_SECRET = "insecure-dev-secret-change-me-before-deploying-anywhere-real"


class Settings(BaseSettings):
    """Centralized application configuration, populated from environment variables."""

    # DevTrack keeps a single .env at the repository root (see .env.example there).
    # Both paths are checked so this works whether uvicorn/pytest is run from
    # the repo root or from backend/.
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DevTrack API"
    # "development" by default so a fresh checkout never accidentally behaves
    # like production; real deployments must set ENVIRONMENT=production
    # explicitly (see .env.production.example).
    environment: str = "development"
    # Safe by default: local dev opts into DEBUG=true via .env rather than
    # every other environment having to opt out of it.
    debug: bool = False

    database_url: str = "postgresql+psycopg2://devtrack:devtrack@localhost:5432/devtrack"

    cors_origins: list[str] = ["http://localhost:5173"]

    # Insecure by design: a working default so local dev/tests don't require
    # a .env file. Every real deployment must override this via environment
    # variables (see .env.example) — enforced below when ENVIRONMENT=production.
    jwt_secret_key: str = _INSECURE_DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        # Many hosting providers (Render, Heroku, etc.) hand out
        # "postgres://..." or driver-less "postgresql://..." connection
        # strings. Normalize to the psycopg2 driver this app actually has
        # installed, so DATABASE_URL works as-is regardless of the host.
        if value.startswith("postgres://"):
            value = "postgresql://" + value.removeprefix("postgres://")
        if value.startswith("postgresql://"):
            value = "postgresql+psycopg2://" + value.removeprefix("postgresql://")
        return value

    @model_validator(mode="after")
    def _require_real_jwt_secret_in_production(self) -> "Settings":
        if self.environment == "production" and self.jwt_secret_key == _INSECURE_DEFAULT_JWT_SECRET:
            raise ValueError(
                "JWT_SECRET_KEY must be set to a real secret when ENVIRONMENT=production. "
                'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
