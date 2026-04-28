from tests.integration.conftest import ADMIN_EMAIL


def test_list_roles_without_token_returns_401(http):
    response = http.get("/api/v1/roles")
    assert response.status_code == 401


def test_list_roles_returns_all_roles(http, admin_headers, admin_role):
    response = http.get("/api/v1/roles", headers=admin_headers)
    assert response.status_code == 200, response.text

    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    assert any(r["name"] == "admin" for r in body)


def test_list_roles_with_attendee_returns_403(http, attendee_headers):
    response = http.get("/api/v1/roles", headers=attendee_headers)
    assert response.status_code == 403
