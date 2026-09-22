import uuid

from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def test_create_project_requires_auth(client: TestClient) -> None:
    response = client.post("/api/projects", json={"name": "DevTrack"})

    assert response.status_code == 401


def test_create_project_creates_owner_membership(client: TestClient) -> None:
    owner, headers = register_and_login(client, "owner1@example.com", "Owner One")

    response = client.post(
        "/api/projects", json={"name": "DevTrack", "description": "Issue tracker"}, headers=headers
    )

    assert response.status_code == 201
    project = response.json()
    assert project["owner_id"] == owner["id"]

    members = client.get(f"/api/projects/{project['id']}/members", headers=headers).json()
    assert len(members) == 1
    assert members[0]["user_id"] == owner["id"]
    assert members[0]["role"] == "owner"


def test_client_cannot_choose_arbitrary_project_owner(client: TestClient) -> None:
    owner, headers = register_and_login(client, "owner2@example.com", "Owner Two")
    someone_else_id = str(uuid.uuid4())

    # owner_id is no longer part of the request schema; supplying it is
    # simply ignored/rejected by validation, never trusted as identity.
    response = client.post(
        "/api/projects",
        json={"name": "Spoofed", "owner_id": someone_else_id},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["owner_id"] == owner["id"]


def test_non_member_cannot_view_project(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner3@example.com", "Owner Three")
    project = client.post("/api/projects", json={"name": "Private"}, headers=owner_headers).json()
    _, outsider_headers = register_and_login(client, "outsider3@example.com", "Outsider")

    response = client.get(f"/api/projects/{project['id']}", headers=outsider_headers)

    assert response.status_code == 403


def test_member_can_view_project(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner4@example.com", "Owner Four")
    project = client.post("/api/projects", json={"name": "Visible"}, headers=owner_headers).json()

    response = client.get(f"/api/projects/{project['id']}", headers=owner_headers)

    assert response.status_code == 200


def test_list_projects_only_shows_own_projects(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner5@example.com", "Owner Five")
    client.post("/api/projects", json={"name": "Mine"}, headers=owner_headers)
    _, outsider_headers = register_and_login(client, "outsider5@example.com", "Outsider")

    response = client.get("/api/projects", headers=outsider_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_get_project_not_found(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner6@example.com", "Owner Six")

    response = client.get(f"/api/projects/{uuid.uuid4()}", headers=headers)

    assert response.status_code == 404


def test_owner_can_update_project(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner7@example.com", "Owner Seven")
    project = client.post("/api/projects", json={"name": "Old Name"}, headers=headers).json()

    response = client.patch(f"/api/projects/{project['id']}", json={"name": "New Name"}, headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_non_owner_member_cannot_update_project(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner8@example.com", "Owner Eight")
    project = client.post("/api/projects", json={"name": "Team Project"}, headers=owner_headers).json()
    member, member_headers = register_and_login(client, "member8@example.com", "Member")
    client.post(
        f"/api/projects/{project['id']}/members", json={"user_id": member["id"]}, headers=owner_headers
    )

    response = client.patch(
        f"/api/projects/{project['id']}", json={"name": "Hijacked"}, headers=member_headers
    )

    assert response.status_code == 403


def test_owner_can_delete_project(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner9@example.com", "Owner Nine")
    project = client.post("/api/projects", json={"name": "Doomed"}, headers=headers).json()

    response = client.delete(f"/api/projects/{project['id']}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/api/projects/{project['id']}", headers=headers)
    assert response.status_code == 404
