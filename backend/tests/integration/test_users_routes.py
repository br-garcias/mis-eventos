def _create_payload(**overrides):
    base = {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "password": "AnotherPass1!",
        "role_name": "admin",
    }
    base.update(overrides)
    return base


def test_create_user_without_token_returns_401(http, admin_role):
    response = http.post("/api/v1/users", json=_create_payload())
    assert response.status_code == 401


def test_create_user_as_admin_returns_201(http, admin_headers):
    response = http.post("/api/v1/users", headers=admin_headers, json=_create_payload())
    assert response.status_code == 201
    assert response.json()["id"]


def test_create_user_duplicate_email_returns_409(http, admin_headers):
    http.post("/api/v1/users", headers=admin_headers, json=_create_payload())
    response = http.post("/api/v1/users", headers=admin_headers, json=_create_payload())
    assert response.status_code == 409


def test_create_user_invalid_email_returns_422_pydantic(http, admin_headers):
    response = http.post("/api/v1/users", headers=admin_headers, json=_create_payload(email="not-an-email"))
    assert response.status_code == 422  # caught by FastAPI/Pydantic before reaching the handler


def test_create_user_short_password_returns_422_domain(http, admin_headers):
    response = http.post("/api/v1/users", headers=admin_headers, json=_create_payload(password="short"))
    assert response.status_code == 422
    body = response.json()
    # Domain-level errors come back via the global DomainValidationError handler
    assert body["code"] == "DomainValidationError"
    assert "password" in body["details"]


def test_create_user_unknown_role_returns_422(http, admin_headers):
    response = http.post("/api/v1/users", headers=admin_headers, json=_create_payload(role_name="ghost"))
    assert response.status_code == 422
    body = response.json()
    assert "role_name" in body["details"]


def test_update_user_404_when_not_found(http, admin_headers):
    response = http.patch("/api/v1/users/00000000-0000-0000-0000-000000000000",
        headers=admin_headers,
        json={"name": "Renamed"},
    )
    assert response.status_code == 404


def test_toggle_user_activates_deactivates(http, admin_headers):
    created = http.post("/api/v1/users", headers=admin_headers, json=_create_payload()).json()
    user_id = created["id"]

    first = http.post(f"/api/v1/users/{user_id}/toggle", headers=admin_headers)
    assert first.status_code == 204

    second = http.post(f"/api/v1/users/{user_id}/toggle", headers=admin_headers)
    assert second.status_code == 204


def test_toggle_user_404(http, admin_headers):
    response = http.post("/api/v1/users/00000000-0000-0000-0000-000000000000/toggle",
        headers=admin_headers,
    )
    assert response.status_code == 404
