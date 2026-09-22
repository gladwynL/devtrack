import uuid

from fastapi.testclient import TestClient


def _create_user(client: TestClient, email: str, name: str) -> dict:
    return client.post("/api/users", json={"email": email, "display_name": name}).json()


def test_create_project_creates_owner_membership(client: TestClient) -> None:
    owner = _create_user(client, "owner1@example.com", "Owner One")

    response = client.post(
        "/api/projects",
        json={"name": "DevTrack", "description": "Issue tracker", "owner_id": owner["id"]},
    )

    assert response.status_code == 201
    project = response.json()
    assert project["owner_id"] == owner["id"]

    members = client.get(f"/api/projects/{project['id']}/members").json()
    assert len(members) == 1
    assert members[0]["user_id"] == owner["id"]
    assert members[0]["role"] == "owner"


def test_get_and_list_project(client: TestClient) -> None:
    owner = _create_user(client, "owner2@example.com", "Owner Two")
    created = client.post("/api/projects", json={"name": "Project Two", "owner_id": owner["id"]}).json()

    response = client.get(f"/api/projects/{created['id']}")
    assert response.status_code == 200

    response = client.get("/api/projects")
    assert response.status_code == 200
    assert any(p["id"] == created["id"] for p in response.json())


def test_get_project_not_found(client: TestClient) -> None:
    response = client.get(f"/api/projects/{uuid.uuid4()}")

    assert response.status_code == 404


def test_create_project_with_nonexistent_owner_rejected(client: TestClient) -> None:
    response = client.post("/api/projects", json={"name": "Orphan", "owner_id": str(uuid.uuid4())})

    assert response.status_code == 400


def test_update_project(client: TestClient) -> None:
    owner = _create_user(client, "owner3@example.com", "Owner Three")
    created = client.post("/api/projects", json={"name": "Old Name", "owner_id": owner["id"]}).json()

    response = client.patch(f"/api/projects/{created['id']}", json={"name": "New Name"})

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
