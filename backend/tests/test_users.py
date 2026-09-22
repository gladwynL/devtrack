import uuid

from fastapi.testclient import TestClient


def test_create_user(client: TestClient) -> None:
    response = client.post("/api/users", json={"email": "alice@example.com", "display_name": "Alice"})

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Alice"
    assert uuid.UUID(body["id"])


def test_create_user_duplicate_email_rejected(client: TestClient) -> None:
    client.post("/api/users", json={"email": "bob@example.com", "display_name": "Bob"})

    response = client.post("/api/users", json={"email": "bob@example.com", "display_name": "Bob Two"})

    assert response.status_code == 409


def test_get_user(client: TestClient) -> None:
    created = client.post("/api/users", json={"email": "carol@example.com", "display_name": "Carol"}).json()

    response = client.get(f"/api/users/{created['id']}")

    assert response.status_code == 200
    assert response.json()["email"] == "carol@example.com"


def test_get_user_not_found(client: TestClient) -> None:
    response = client.get(f"/api/users/{uuid.uuid4()}")

    assert response.status_code == 404


def test_update_user(client: TestClient) -> None:
    created = client.post("/api/users", json={"email": "dan@example.com", "display_name": "Dan"}).json()

    response = client.patch(f"/api/users/{created['id']}", json={"display_name": "Daniel"})

    assert response.status_code == 200
    assert response.json()["display_name"] == "Daniel"


def test_delete_user(client: TestClient) -> None:
    created = client.post("/api/users", json={"email": "erin@example.com", "display_name": "Erin"}).json()

    response = client.delete(f"/api/users/{created['id']}")
    assert response.status_code == 204

    response = client.get(f"/api/users/{created['id']}")
    assert response.status_code == 404


def test_delete_user_restricted_while_owning_a_project(client: TestClient) -> None:
    owner = client.post("/api/users", json={"email": "frank@example.com", "display_name": "Frank"}).json()
    client.post("/api/projects", json={"name": "Owned Project", "owner_id": owner["id"]})

    response = client.delete(f"/api/users/{owner['id']}")

    assert response.status_code == 409
