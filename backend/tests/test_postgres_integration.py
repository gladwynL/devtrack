"""Integration check against a real, Alembic-migrated PostgreSQL database.

The rest of the suite deliberately runs against fast, isolated in-memory
SQLite (see conftest.py) so day-to-day `pytest` runs need nothing else
running. This file is the one exception: it exercises the real service
layer (ORM models + Argon2 hashing) against actual PostgreSQL to catch any
dialect-specific issues SQLite wouldn't surface. It only runs when
POSTGRES_TEST_DATABASE_URL is set, so it's opt-in locally and in CI.

Run it locally with Postgres up (see docker-compose.yml):

    POSTGRES_TEST_DATABASE_URL=postgresql+psycopg2://devtrack:devtrack@localhost:5432/devtrack \
        venv/Scripts/python -m pytest tests/test_postgres_integration.py -v
"""

import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

POSTGRES_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not POSTGRES_URL,
    reason="Set POSTGRES_TEST_DATABASE_URL to a real PostgreSQL instance to run this test.",
)


def test_register_and_authenticate_user_against_real_postgresql() -> None:
    from app.models.user import User
    from app.schemas.auth import LoginRequest, RegisterRequest
    from app.services.auth import authenticate_user, register_user

    engine = create_engine(POSTGRES_URL)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()

    email = f"pg-integration-{uuid.uuid4()}@example.com"
    try:
        created = register_user(
            db, RegisterRequest(email=email, display_name="PG Integration", password="password123")
        )
        assert created.id is not None
        assert created.password_hash.startswith("$argon2")

        authenticated = authenticate_user(db, LoginRequest(email=email, password="password123"))
        assert authenticated.id == created.id
    finally:
        stored = db.query(User).filter(User.email == email).first()
        if stored:
            db.delete(stored)
            db.commit()
        db.close()
        engine.dispose()
