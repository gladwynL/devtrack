import uuid

from fastapi.testclient import TestClient


def _create_user(client: TestClient, email: str, name: str) -> dict:
    return client.post("/api/users", json={"email": email, "display_name": name}).json()


def _create_project(client: TestClient, owner_id: str, name: str = "Project") -> dict:
    return client.post("/api/projects", json={"name": name, "owner_id": owner_id}).json()


def test_create_issue(client: TestClient) -> None:
    owner = _create_user(client, "owner1@example.com", "Owner")
    project = _create_project(client, owner["id"])

    response = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": "Bug", "created_by_id": owner["id"]},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "todo"
    assert body["priority"] == "medium"
    assert body["project_id"] == project["id"]


def test_create_issue_not_found_project(client: TestClient) -> None:
    owner = _create_user(client, "owner2@example.com", "Owner")

    response = client.post(
        f"/api/projects/{uuid.uuid4()}/issues",
        json={"title": "Bug", "created_by_id": owner["id"]},
    )

    assert response.status_code == 404


def test_create_issue_creator_must_be_project_member(client: TestClient) -> None:
    owner = _create_user(client, "owner3@example.com", "Owner")
    project = _create_project(client, owner["id"])
    outsider = _create_user(client, "outsider3@example.com", "Outsider")

    response = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": "Bug", "created_by_id": outsider["id"]},
    )

    assert response.status_code == 400


def test_create_issue_assignee_must_be_project_member(client: TestClient) -> None:
    owner = _create_user(client, "owner4@example.com", "Owner")
    project = _create_project(client, owner["id"])
    outsider = _create_user(client, "outsider4@example.com", "Outsider")

    response = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": "Bug", "created_by_id": owner["id"], "assignee_id": outsider["id"]},
    )

    assert response.status_code == 400


def test_list_project_issues(client: TestClient) -> None:
    owner = _create_user(client, "owner5@example.com", "Owner")
    project = _create_project(client, owner["id"])
    client.post(f"/api/projects/{project['id']}/issues", json={"title": "One", "created_by_id": owner["id"]})
    client.post(f"/api/projects/{project['id']}/issues", json={"title": "Two", "created_by_id": owner["id"]})

    response = client.get(f"/api/projects/{project['id']}/issues")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_issue_status_and_priority(client: TestClient) -> None:
    owner = _create_user(client, "owner6@example.com", "Owner")
    project = _create_project(client, owner["id"])
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Task", "created_by_id": owner["id"]}
    ).json()

    response = client.patch(f"/api/issues/{issue['id']}", json={"status": "in_progress", "priority": "high"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "in_progress"
    assert body["priority"] == "high"


def test_update_issue_assignee_must_be_project_member(client: TestClient) -> None:
    owner = _create_user(client, "owner7@example.com", "Owner")
    project = _create_project(client, owner["id"])
    outsider = _create_user(client, "outsider7@example.com", "Outsider")
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Task", "created_by_id": owner["id"]}
    ).json()

    response = client.patch(f"/api/issues/{issue['id']}", json={"assignee_id": outsider["id"]})

    assert response.status_code == 400


def test_delete_issue(client: TestClient) -> None:
    owner = _create_user(client, "owner8@example.com", "Owner")
    project = _create_project(client, owner["id"])
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Task", "created_by_id": owner["id"]}
    ).json()

    response = client.delete(f"/api/issues/{issue['id']}")
    assert response.status_code == 204

    response = client.get(f"/api/issues/{issue['id']}")
    assert response.status_code == 404


def test_get_issue_not_found(client: TestClient) -> None:
    response = client.get(f"/api/issues/{uuid.uuid4()}")

    assert response.status_code == 404


def test_create_issue_invalid_status_returns_validation_error(client: TestClient) -> None:
    owner = _create_user(client, "owner9@example.com", "Owner")
    project = _create_project(client, owner["id"])

    response = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": "Task", "created_by_id": owner["id"], "status": "not_a_status"},
    )

    assert response.status_code == 422


def test_create_issue_missing_title_returns_validation_error(client: TestClient) -> None:
    owner = _create_user(client, "owner10@example.com", "Owner")
    project = _create_project(client, owner["id"])

    response = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"created_by_id": owner["id"]},
    )

    assert response.status_code == 422
