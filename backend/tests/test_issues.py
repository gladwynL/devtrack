import uuid

from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def _create_project(client: TestClient, headers: dict, name: str = "Project") -> dict:
    return client.post("/api/projects", json={"name": name}, headers=headers).json()


def _add_member(client: TestClient, project_id: str, owner_headers: dict, user_id: str) -> None:
    client.post(f"/api/projects/{project_id}/members", json={"user_id": user_id}, headers=owner_headers)


def test_create_issue_requires_membership(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner1@example.com", "Owner")
    project = _create_project(client, owner_headers)
    _, outsider_headers = register_and_login(client, "outsider1@example.com", "Outsider")

    response = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Bug"}, headers=outsider_headers
    )

    assert response.status_code == 403


def test_create_issue_creator_derived_from_current_user(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner2@example.com", "Owner")
    project = _create_project(client, owner_headers)

    response = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Bug"}, headers=owner_headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["created_by_id"] == owner["id"]
    assert body["status"] == "todo"
    assert body["priority"] == "medium"


def test_member_cannot_impersonate_another_creator(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner3@example.com", "Owner")
    project = _create_project(client, owner_headers)
    member, member_headers = register_and_login(client, "member3@example.com", "Member")
    _add_member(client, project["id"], owner_headers, member["id"])

    # created_by_id is no longer part of the request schema; even if a
    # client tries to sneak it in, the creator is always the caller.
    response = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": "Bug", "created_by_id": owner["id"]},
        headers=member_headers,
    )

    assert response.status_code == 201
    assert response.json()["created_by_id"] == member["id"]


def test_create_issue_assignee_must_be_project_member(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner4@example.com", "Owner")
    project = _create_project(client, owner_headers)
    outsider, _ = register_and_login(client, "outsider4@example.com", "Outsider")

    response = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": "Bug", "assignee_id": outsider["id"]},
        headers=owner_headers,
    )

    assert response.status_code == 400


def test_non_member_cannot_list_project_issues(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner5@example.com", "Owner")
    project = _create_project(client, owner_headers)
    _, outsider_headers = register_and_login(client, "outsider5@example.com", "Outsider")

    response = client.get(f"/api/projects/{project['id']}/issues", headers=outsider_headers)

    assert response.status_code == 403


def test_member_can_list_project_issues(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner6@example.com", "Owner")
    project = _create_project(client, owner_headers)
    client.post(f"/api/projects/{project['id']}/issues", json={"title": "One"}, headers=owner_headers)
    client.post(f"/api/projects/{project['id']}/issues", json={"title": "Two"}, headers=owner_headers)

    response = client.get(f"/api/projects/{project['id']}/issues", headers=owner_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_non_member_cannot_view_issue(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner7@example.com", "Owner")
    project = _create_project(client, owner_headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Task"}, headers=owner_headers
    ).json()
    _, outsider_headers = register_and_login(client, "outsider7@example.com", "Outsider")

    response = client.get(f"/api/issues/{issue['id']}", headers=outsider_headers)

    assert response.status_code == 403


def test_member_can_update_issue_status_and_priority(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner8@example.com", "Owner")
    project = _create_project(client, owner_headers)
    member, member_headers = register_and_login(client, "member8@example.com", "Member")
    _add_member(client, project["id"], owner_headers, member["id"])
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Task"}, headers=owner_headers
    ).json()

    response = client.patch(
        f"/api/issues/{issue['id']}",
        json={"status": "in_progress", "priority": "high"},
        headers=member_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "in_progress"
    assert body["priority"] == "high"


def test_non_member_cannot_update_issue(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner9@example.com", "Owner")
    project = _create_project(client, owner_headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Task"}, headers=owner_headers
    ).json()
    _, outsider_headers = register_and_login(client, "outsider9@example.com", "Outsider")

    response = client.patch(f"/api/issues/{issue['id']}", json={"status": "done"}, headers=outsider_headers)

    assert response.status_code == 403


def test_update_issue_assignee_must_be_project_member(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner10@example.com", "Owner")
    project = _create_project(client, owner_headers)
    outsider, _ = register_and_login(client, "outsider10@example.com", "Outsider")
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Task"}, headers=owner_headers
    ).json()

    response = client.patch(
        f"/api/issues/{issue['id']}", json={"assignee_id": outsider["id"]}, headers=owner_headers
    )

    assert response.status_code == 400


def test_member_can_delete_issue(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner11@example.com", "Owner")
    project = _create_project(client, owner_headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Task"}, headers=owner_headers
    ).json()

    response = client.delete(f"/api/issues/{issue['id']}", headers=owner_headers)
    assert response.status_code == 204

    response = client.get(f"/api/issues/{issue['id']}", headers=owner_headers)
    assert response.status_code == 404


def test_non_member_cannot_delete_issue(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner12@example.com", "Owner")
    project = _create_project(client, owner_headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Task"}, headers=owner_headers
    ).json()
    _, outsider_headers = register_and_login(client, "outsider12@example.com", "Outsider")

    response = client.delete(f"/api/issues/{issue['id']}", headers=outsider_headers)

    assert response.status_code == 403


def test_get_issue_not_found(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner13@example.com", "Owner")

    response = client.get(f"/api/issues/{uuid.uuid4()}", headers=headers)

    assert response.status_code == 404


def test_create_issue_invalid_status_returns_validation_error(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner14@example.com", "Owner")
    project = _create_project(client, headers)

    response = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": "Task", "status": "not_a_status"},
        headers=headers,
    )

    assert response.status_code == 422


def test_create_issue_missing_title_returns_validation_error(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner15@example.com", "Owner")
    project = _create_project(client, headers)

    response = client.post(f"/api/projects/{project['id']}/issues", json={}, headers=headers)

    assert response.status_code == 422


def test_list_project_issues_pagination_query_params_validated(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner16@example.com", "Owner")
    project = _create_project(client, headers)

    base = f"/api/projects/{project['id']}/issues"
    assert client.get(f"{base}?offset=-1", headers=headers).status_code == 422
    assert client.get(f"{base}?limit=0", headers=headers).status_code == 422
    assert client.get(f"{base}?limit=1000", headers=headers).status_code == 422
