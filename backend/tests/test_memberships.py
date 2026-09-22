from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def _create_project(client: TestClient, headers: dict, name: str = "Project") -> dict:
    return client.post("/api/projects", json={"name": name}, headers=headers).json()


def test_owner_can_add_member(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner1@example.com", "Owner")
    project = _create_project(client, owner_headers)
    member, _ = register_and_login(client, "member1@example.com", "Member")

    response = client.post(
        f"/api/projects/{project['id']}/members", json={"user_id": member["id"]}, headers=owner_headers
    )

    assert response.status_code == 201
    assert response.json()["role"] == "member"


def test_non_owner_cannot_add_member(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner2@example.com", "Owner")
    project = _create_project(client, owner_headers)
    member, member_headers = register_and_login(client, "member2@example.com", "Member")
    client.post(
        f"/api/projects/{project['id']}/members", json={"user_id": member["id"]}, headers=owner_headers
    )
    outsider, _ = register_and_login(client, "outsider2@example.com", "Outsider")

    response = client.post(
        f"/api/projects/{project['id']}/members", json={"user_id": outsider["id"]}, headers=member_headers
    )

    assert response.status_code == 403


def test_duplicate_membership_rejected(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner3@example.com", "Owner")
    project = _create_project(client, owner_headers)

    # The project owner already has an owner membership from project creation.
    response = client.post(
        f"/api/projects/{project['id']}/members", json={"user_id": owner["id"]}, headers=owner_headers
    )

    assert response.status_code == 409


def test_member_can_list_members(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner4@example.com", "Owner")
    project = _create_project(client, owner_headers)
    member, member_headers = register_and_login(client, "member4@example.com", "Member")
    client.post(
        f"/api/projects/{project['id']}/members", json={"user_id": member["id"]}, headers=owner_headers
    )

    response = client.get(f"/api/projects/{project['id']}/members", headers=member_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_non_member_cannot_list_members(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner5@example.com", "Owner")
    project = _create_project(client, owner_headers)
    _, outsider_headers = register_and_login(client, "outsider5@example.com", "Outsider")

    response = client.get(f"/api/projects/{project['id']}/members", headers=outsider_headers)

    assert response.status_code == 403


def test_owner_can_remove_member(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner6@example.com", "Owner")
    project = _create_project(client, owner_headers)
    member, _ = register_and_login(client, "member6@example.com", "Member")
    client.post(
        f"/api/projects/{project['id']}/members", json={"user_id": member["id"]}, headers=owner_headers
    )

    response = client.delete(f"/api/projects/{project['id']}/members/{member['id']}", headers=owner_headers)
    assert response.status_code == 204

    members = client.get(f"/api/projects/{project['id']}/members", headers=owner_headers).json()
    assert len(members) == 1


def test_non_owner_cannot_remove_member(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner7@example.com", "Owner")
    project = _create_project(client, owner_headers)
    member, member_headers = register_and_login(client, "member7@example.com", "Member")
    client.post(
        f"/api/projects/{project['id']}/members", json={"user_id": member["id"]}, headers=owner_headers
    )

    response = client.delete(f"/api/projects/{project['id']}/members/{member['id']}", headers=member_headers)

    assert response.status_code == 403


def test_owner_cannot_be_removed(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner8@example.com", "Owner")
    project = _create_project(client, owner_headers)

    response = client.delete(f"/api/projects/{project['id']}/members/{owner['id']}", headers=owner_headers)

    assert response.status_code == 400
