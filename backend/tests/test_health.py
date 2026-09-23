from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert "app_name" in body
    assert "environment" in body


def test_ready_returns_ok_when_database_is_reachable() -> None:
    response = client.get("/ready")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
