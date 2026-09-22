from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 registers model metadata on Base
from app.db.session import Base, get_db
from app.main import app

# In-memory SQLite, kept alive for the whole test session via StaticPool
# (a fresh in-memory DB would otherwise be created per-connection). This
# keeps tests fast and independent of a running PostgreSQL instance while
# staying schema-compatible with the portable column/constraint types used
# in the models (see app/models/*.py).
_test_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(_test_engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
    # SQLite ignores foreign key constraints (including ON DELETE
    # RESTRICT/CASCADE/SET NULL) unless explicitly enabled per connection.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def _override_get_db() -> Generator[Session, None, None]:
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def _reset_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Direct access to the test database, for assertions the API can't expose (e.g. stored hashes)."""
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def register_and_login(
    client: TestClient, email: str, display_name: str, password: str = "password123"
) -> tuple[dict, dict]:
    """Registers a user, logs in, and returns (user dict, auth headers)."""
    client.post(
        "/api/auth/register",
        json={"email": email, "display_name": display_name, "password": password},
    )
    login_response = client.post("/api/auth/login", json={"email": email, "password": password})
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    me = client.get("/api/auth/me", headers=headers).json()
    return me, headers
