from app.core.config import Settings


def test_database_url_normalizes_bare_postgres_scheme() -> None:
    settings = Settings(database_url="postgres://user:pass@host/db")

    assert settings.database_url == "postgresql+psycopg2://user:pass@host/db"


def test_database_url_normalizes_driverless_postgresql_scheme() -> None:
    settings = Settings(database_url="postgresql://user:pass@host/db")

    assert settings.database_url == "postgresql+psycopg2://user:pass@host/db"


def test_database_url_left_untouched_when_driver_already_specified() -> None:
    settings = Settings(database_url="postgresql+psycopg2://user:pass@host/db")

    assert settings.database_url == "postgresql+psycopg2://user:pass@host/db"


def test_production_requires_a_real_jwt_secret() -> None:
    try:
        Settings(environment="production")
    except ValueError as exc:
        assert "JWT_SECRET_KEY" in str(exc)
    else:
        raise AssertionError("Expected Settings() to reject the default JWT secret in production.")


def test_production_accepts_a_real_jwt_secret() -> None:
    settings = Settings(environment="production", jwt_secret_key="a-real-secret-value")

    assert settings.environment == "production"
