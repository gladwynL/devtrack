import uuid

from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def _create_project(client: TestClient, headers: dict, name: str = "Project") -> dict:
    return client.post("/api/projects", json={"name": name}, headers=headers).json()


def _add_member(client: TestClient, project_id: str, owner_headers: dict, user_id: str) -> None:
    client.post(f"/api/projects/{project_id}/members", json={"user_id": user_id}, headers=owner_headers)


def test_activity_created_on_issue_creation(client: TestClient) -> None:
    owner, headers = register_and_login(client, "owner1@example.com", "Owner")
    project = _create_project(client, headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Bug"}, headers=headers
    ).json()

    response = client.get(f"/api/issues/{issue['id']}/activity", headers=headers)

    assert response.status_code == 200
    entries = response.json()
    assert len(entries) == 1
    assert entries[0]["event_type"] == "created"
    assert entries[0]["actor_id"] == owner["id"]
    assert entries[0]["field_name"] is None


def test_activity_created_for_field_updates(client: TestClient) -> None:
    owner, headers = register_and_login(client, "owner2@example.com", "Owner")
    project = _create_project(client, headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Bug"}, headers=headers
    ).json()

    client.patch(
        f"/api/issues/{issue['id']}",
        json={"status": "in_progress", "priority": "high", "title": "Bug (renamed)"},
        headers=headers,
    )

    response = client.get(f"/api/issues/{issue['id']}/activity", headers=headers)
    entries = response.json()

    event_types = {entry["event_type"] for entry in entries}
    assert event_types == {"created", "status_changed", "priority_changed", "title_changed"}

    status_entry = next(e for e in entries if e["event_type"] == "status_changed")
    assert status_entry["field_name"] == "status"
    assert status_entry["old_value"] == "todo"
    assert status_entry["new_value"] == "in_progress"
    assert status_entry["actor_id"] == owner["id"]


def test_description_change_recorded_without_content(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner3@example.com", "Owner")
    project = _create_project(client, headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": "Bug", "description": "Original text"},
        headers=headers,
    ).json()

    client.patch(f"/api/issues/{issue['id']}", json={"description": "Updated text"}, headers=headers)

    entries = client.get(f"/api/issues/{issue['id']}/activity", headers=headers).json()
    description_entry = next(e for e in entries if e["event_type"] == "description_changed")

    assert description_entry["field_name"] == "description"
    assert description_entry["old_value"] is None
    assert description_entry["new_value"] is None


def test_no_activity_entry_for_unchanged_fields(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner4@example.com", "Owner")
    project = _create_project(client, headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": "Bug", "status": "todo", "priority": "medium"},
        headers=headers,
    ).json()

    # Same values as already set: should not produce new activity entries.
    client.patch(f"/api/issues/{issue['id']}", json={"status": "todo", "priority": "medium"}, headers=headers)

    entries = client.get(f"/api/issues/{issue['id']}/activity", headers=headers).json()

    assert len(entries) == 1
    assert entries[0]["event_type"] == "created"


def test_assignee_changed_activity_uses_member_ids(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner5@example.com", "Owner")
    project = _create_project(client, owner_headers)
    member, _ = register_and_login(client, "member5@example.com", "Member")
    _add_member(client, project["id"], owner_headers, member["id"])
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Bug"}, headers=owner_headers
    ).json()

    client.patch(f"/api/issues/{issue['id']}", json={"assignee_id": member["id"]}, headers=owner_headers)

    entries = client.get(f"/api/issues/{issue['id']}/activity", headers=owner_headers).json()
    assignee_entry = next(e for e in entries if e["event_type"] == "assignee_changed")

    assert assignee_entry["old_value"] is None
    assert assignee_entry["new_value"] == member["id"]


def test_actor_derived_from_authenticated_user(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "owner6@example.com", "Owner")
    project = _create_project(client, owner_headers)
    member, member_headers = register_and_login(client, "member6@example.com", "Member")
    _add_member(client, project["id"], owner_headers, member["id"])
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Bug"}, headers=owner_headers
    ).json()

    # The member updates the issue; the actor recorded must be the member,
    # not the issue creator, and there is no way for the client to spoof this.
    client.patch(f"/api/issues/{issue['id']}", json={"status": "done"}, headers=member_headers)

    entries = client.get(f"/api/issues/{issue['id']}/activity", headers=owner_headers).json()
    status_entry = next(e for e in entries if e["event_type"] == "status_changed")

    assert status_entry["actor_id"] == member["id"]
    assert status_entry["actor_id"] != owner["id"]


def test_non_member_cannot_access_activity(client: TestClient) -> None:
    _, owner_headers = register_and_login(client, "owner7@example.com", "Owner")
    project = _create_project(client, owner_headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Bug"}, headers=owner_headers
    ).json()
    _, outsider_headers = register_and_login(client, "outsider7@example.com", "Outsider")

    response = client.get(f"/api/issues/{issue['id']}/activity", headers=outsider_headers)

    assert response.status_code == 403


def test_activity_requires_auth(client: TestClient) -> None:
    response = client.get(f"/api/issues/{uuid.uuid4()}/activity")

    assert response.status_code == 401


def test_activity_not_found_for_missing_issue(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner8@example.com", "Owner")

    response = client.get(f"/api/issues/{uuid.uuid4()}/activity", headers=headers)

    assert response.status_code == 404


def test_activity_order_is_chronological(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner9@example.com", "Owner")
    project = _create_project(client, headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Bug"}, headers=headers
    ).json()

    client.patch(f"/api/issues/{issue['id']}", json={"status": "in_progress"}, headers=headers)
    client.patch(f"/api/issues/{issue['id']}", json={"status": "done"}, headers=headers)

    entries = client.get(f"/api/issues/{issue['id']}/activity", headers=headers).json()
    timestamps = [entry["created_at"] for entry in entries]

    assert [e["event_type"] for e in entries] == ["created", "status_changed", "status_changed"]
    assert timestamps == sorted(timestamps)


def test_activity_pagination_query_params_validated(client: TestClient) -> None:
    _, headers = register_and_login(client, "owner10@example.com", "Owner")
    project = _create_project(client, headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Bug"}, headers=headers
    ).json()

    negative_offset = client.get(f"/api/issues/{issue['id']}/activity?offset=-1", headers=headers)
    zero_limit = client.get(f"/api/issues/{issue['id']}/activity?limit=0", headers=headers)
    too_large_limit = client.get(f"/api/issues/{issue['id']}/activity?limit=1000", headers=headers)

    assert negative_offset.status_code == 422
    assert zero_limit.status_code == 422
    assert too_large_limit.status_code == 422
