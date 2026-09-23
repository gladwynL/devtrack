import uuid

from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def test_list_users_requires_auth(client: TestClient) -> None:
    response = client.get("/api/users")

    assert response.status_code == 401


def test_list_users_authenticated(client: TestClient) -> None:
    _, headers = register_and_login(client, "alice@example.com", "Alice")

    response = client.get("/api/users", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_user_requires_auth(client: TestClient) -> None:
    user, _ = register_and_login(client, "bob@example.com", "Bob")

    response = client.get(f"/api/users/{user['id']}")

    assert response.status_code == 401


def test_get_user_authenticated(client: TestClient) -> None:
    user, _ = register_and_login(client, "carol@example.com", "Carol")
    _, other_headers = register_and_login(client, "dan@example.com", "Dan")

    response = client.get(f"/api/users/{user['id']}", headers=other_headers)

    assert response.status_code == 200
    assert response.json()["email"] == "carol@example.com"
    assert "password_hash" not in response.json()


def test_get_user_not_found(client: TestClient) -> None:
    _, headers = register_and_login(client, "erin@example.com", "Erin")

    response = client.get(f"/api/users/{uuid.uuid4()}", headers=headers)

    assert response.status_code == 404


def test_update_own_user(client: TestClient) -> None:
    user, headers = register_and_login(client, "frank@example.com", "Frank")

    response = client.patch(f"/api/users/{user['id']}", json={"display_name": "Franklin"}, headers=headers)

    assert response.status_code == 200
    assert response.json()["display_name"] == "Franklin"


def test_cannot_update_another_users_account(client: TestClient) -> None:
    victim, _ = register_and_login(client, "grace@example.com", "Grace")
    _, attacker_headers = register_and_login(client, "henry@example.com", "Henry")

    response = client.patch(
        f"/api/users/{victim['id']}", json={"display_name": "Hijacked"}, headers=attacker_headers
    )

    assert response.status_code == 403


def test_delete_own_user(client: TestClient) -> None:
    user, headers = register_and_login(client, "iris@example.com", "Iris")

    response = client.delete(f"/api/users/{user['id']}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/api/users/{user['id']}", headers=headers)
    assert response.status_code == 401  # the deleted user's token no longer resolves


def test_cannot_delete_another_users_account(client: TestClient) -> None:
    victim, _ = register_and_login(client, "jack@example.com", "Jack")
    _, attacker_headers = register_and_login(client, "kim@example.com", "Kim")

    response = client.delete(f"/api/users/{victim['id']}", headers=attacker_headers)

    assert response.status_code == 403


def test_delete_user_restricted_while_owning_a_project(client: TestClient) -> None:
    owner, owner_headers = register_and_login(client, "liam@example.com", "Liam")
    client.post("/api/projects", json={"name": "Owned Project"}, headers=owner_headers)

    response = client.delete(f"/api/users/{owner['id']}", headers=owner_headers)

    assert response.status_code == 409


def test_list_users_pagination_query_params_validated(client: TestClient) -> None:
    _, headers = register_and_login(client, "mia@example.com", "Mia")

    assert client.get("/api/users?offset=-1", headers=headers).status_code == 422
    assert client.get("/api/users?limit=0", headers=headers).status_code == 422
    assert client.get("/api/users?limit=1000", headers=headers).status_code == 422
