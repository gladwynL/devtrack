from fastapi.testclient import TestClient


def _create_user(client: TestClient, email: str, name: str) -> dict:
    return client.post("/api/users", json={"email": email, "display_name": name}).json()


def _create_project(client: TestClient, owner_id: str, name: str = "Project") -> dict:
    return client.post("/api/projects", json={"name": name, "owner_id": owner_id}).json()


def test_add_member(client: TestClient) -> None:
    owner = _create_user(client, "owner1@example.com", "Owner")
    project = _create_project(client, owner["id"])
    member = _create_user(client, "member1@example.com", "Member")

    response = client.post(f"/api/projects/{project['id']}/members", json={"user_id": member["id"]})

    assert response.status_code == 201
    assert response.json()["role"] == "member"


def test_duplicate_membership_rejected(client: TestClient) -> None:
    owner = _create_user(client, "owner2@example.com", "Owner")
    project = _create_project(client, owner["id"])

    # The project owner already has an owner membership from project creation.
    response = client.post(f"/api/projects/{project['id']}/members", json={"user_id": owner["id"]})

    assert response.status_code == 409


def test_list_members(client: TestClient) -> None:
    owner = _create_user(client, "owner3@example.com", "Owner")
    project = _create_project(client, owner["id"])
    member = _create_user(client, "member3@example.com", "Member")
    client.post(f"/api/projects/{project['id']}/members", json={"user_id": member["id"]})

    response = client.get(f"/api/projects/{project['id']}/members")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_remove_member(client: TestClient) -> None:
    owner = _create_user(client, "owner4@example.com", "Owner")
    project = _create_project(client, owner["id"])
    member = _create_user(client, "member4@example.com", "Member")
    client.post(f"/api/projects/{project['id']}/members", json={"user_id": member["id"]})

    response = client.delete(f"/api/projects/{project['id']}/members/{member['id']}")
    assert response.status_code == 204

    members = client.get(f"/api/projects/{project['id']}/members").json()
    assert len(members) == 1


def test_remove_member_not_found(client: TestClient) -> None:
    owner = _create_user(client, "owner5@example.com", "Owner")
    project = _create_project(client, owner["id"])
    outsider = _create_user(client, "outsider5@example.com", "Outsider")

    response = client.delete(f"/api/projects/{project['id']}/members/{outsider['id']}")

    assert response.status_code == 404


def test_owner_cannot_be_removed(client: TestClient) -> None:
    owner = _create_user(client, "owner6@example.com", "Owner")
    project = _create_project(client, owner["id"])

    response = client.delete(f"/api/projects/{project['id']}/members/{owner['id']}")

    assert response.status_code == 400
