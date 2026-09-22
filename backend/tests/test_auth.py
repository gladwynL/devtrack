from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user import User
from tests.conftest import register_and_login


def test_register_succeeds(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "display_name": "Alice", "password": "password123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Alice"
    assert "password" not in body
    assert "password_hash" not in body


def test_password_is_stored_hashed(client: TestClient, db_session: Session) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "bob@example.com", "display_name": "Bob", "password": "password123"},
    )

    user = db_session.scalar(select(User).where(User.email == "bob@example.com"))

    assert user is not None
    assert user.password_hash != "password123"
    assert user.password_hash.startswith("$argon2")


def test_duplicate_registration_rejected(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "carol@example.com", "display_name": "Carol", "password": "password123"},
    )

    response = client.post(
        "/api/auth/register",
        json={"email": "carol@example.com", "display_name": "Carol Two", "password": "password456"},
    )

    assert response.status_code == 409


def test_register_rejects_short_password(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "dan@example.com", "display_name": "Dan", "password": "short"},
    )

    assert response.status_code == 422


def test_login_succeeds_with_correct_credentials(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "erin@example.com", "display_name": "Erin", "password": "password123"},
    )

    response = client.post("/api/auth/login", json={"email": "erin@example.com", "password": "password123"})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_rejected_with_wrong_password(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "frank@example.com", "display_name": "Frank", "password": "password123"},
    )

    response = client.post("/api/auth/login", json={"email": "frank@example.com", "password": "wrongpass"})

    assert response.status_code == 401


def test_login_rejected_for_unknown_email(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "password123"})

    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient) -> None:
    user, headers = register_and_login(client, "grace@example.com", "Grace")

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == user["id"]
    assert response.json()["email"] == "grace@example.com"


def test_me_without_token_rejected(client: TestClient) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token_rejected(client: TestClient) -> None:
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401


def test_me_with_malformed_authorization_header_rejected(client: TestClient) -> None:
    response = client.get("/api/auth/me", headers={"Authorization": "not-even-bearer-shaped"})

    assert response.status_code == 401


def test_me_with_expired_token_rejected(client: TestClient) -> None:
    _, headers = register_and_login(client, "henry@example.com", "Henry")
    user_id = client.get("/api/auth/me", headers=headers).json()["id"]

    settings = get_settings()
    expired_payload = {"sub": user_id, "exp": datetime.now(UTC) - timedelta(minutes=1)}
    expired_token = jwt.encode(expired_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401
