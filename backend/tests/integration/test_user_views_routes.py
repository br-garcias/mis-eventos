from .conftest import ADMIN_EMAIL


def _create_user(http, headers, *, name="Bob", email="bob@example.com",
                 password="AnotherPass1!", role_name="admin"):
    response = http.post("/api/v1/users", headers=headers, json={
        "name": name,
        "email": email,
        "password": password,
        "role_name": role_name,
    })
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_search_users_without_token_returns_401(http):
    response = http.get("/api/v1/users")
    assert response.status_code == 401


def test_search_users_returns_admin_seed(http, admin_headers, admin_user):
    response = http.get("/api/v1/users", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    items = body["items"]
    assert any(u["email"] == ADMIN_EMAIL for u in items)
    admin = next(u for u in items if u["email"] == ADMIN_EMAIL)
    assert admin["role"]["name"] == "admin"
    assert admin["is_active"] is True


def test_search_users_filters_by_email(http, admin_headers, admin_user):
    _create_user(http, admin_headers, email="bob@example.com")
    _create_user(http, admin_headers, email="carol@example.com")

    response = http.get("/api/v1/users?email=carol@example.com", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert [u["email"] for u in body["items"]] == ["carol@example.com"]


def test_search_users_filters_by_role_id(http, admin_headers, admin_user, admin_role):
    _create_user(http, admin_headers, email="bob@example.com")

    response = http.get(f"/api/v1/users?role_id={admin_role.id.value}", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    emails = sorted(u["email"] for u in body["items"])
    assert ADMIN_EMAIL in emails
    assert "bob@example.com" in emails


def test_search_users_combines_filters(http, admin_headers, admin_user, admin_role):
    _create_user(http, admin_headers, email="bob@example.com")

    response = http.get(f"/api/v1/users?email=bob@example.com&role_id={admin_role.id.value}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert [u["email"] for u in body["items"]] == ["bob@example.com"]


def test_find_user_by_id_returns_404_when_missing(http, admin_headers):
    response = http.get("/api/v1/users/00000000-0000-0000-0000-000000000000",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_find_user_by_id_includes_role(http, admin_headers, admin_user):
    response = http.get(f"/api/v1/users/{admin_user.id.value}", headers=admin_headers)
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["id"] == admin_user.id.value
    assert body["email"] == ADMIN_EMAIL
    assert body["role"]["name"] == "admin"
