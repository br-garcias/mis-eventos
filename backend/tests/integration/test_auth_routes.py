from .conftest import ADMIN_EMAIL, ADMIN_PASSWORD


def test_health(http):
    response = http.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["components"]["api"] == "ok"
    assert body["components"]["mongo"] == "ok"


def test_login_unknown_user_returns_401(http):
    response = http.post("/api/v1/auth/login", json={"email": "ghost@example.com", "password": "whatever"})
    assert response.status_code == 401


def test_login_wrong_password_returns_401(http, admin_user):
    response = http.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": "nope"})
    assert response.status_code == 401


def test_login_success_returns_token_pair(http, admin_user):
    response = http.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["session_id"]
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["access_token_expiry"] > 0
    assert body["refresh_token_expiry"] > body["access_token_expiry"]


def test_me_without_token_returns_401(http):
    response = http.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_token_returns_identity(http, admin_user, admin_headers):
    response = http.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == admin_user.id.value
    assert body["name"] == admin_user.name.value
    assert body["email"] == admin_user.email.value
    assert body["is_active"] is True
    assert body["role"]["role"] == "admin"


def test_refresh_returns_new_tokens(http, admin_tokens):
    response = http.post("/api/v1/auth/refresh", json={"refresh_token": admin_tokens["refresh_token"]})
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] != admin_tokens["access_token"]
    assert body["refresh_token"] != admin_tokens["refresh_token"]


def test_refresh_with_invalid_token_returns_401(http):
    response = http.post("/api/v1/auth/refresh", json={"refresh_token": "garbage"})
    assert response.status_code == 401


def test_logout_revokes_session(http, admin_tokens, admin_headers):
    logout = http.post("/api/v1/auth/logout", headers=admin_headers)
    assert logout.status_code == 204

    refresh = http.post("/api/v1/auth/refresh", json={"refresh_token": admin_tokens["refresh_token"]})
    assert refresh.status_code == 401


# ── Public registration ──────────────────────────────────────────────────────
def test_register_creates_attendee_and_returns_tokens(http, attendee_role):
    response = http.post("/api/v1/auth/register", json={
        "name": "New User",
        "email": "newbie@example.com",
        "password": "Sup3rSecret!",
    })
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["session_id"]
    assert body["access_token"]
    assert body["refresh_token"]


def test_register_then_me_exposes_role_attendee(http, attendee_role):
    register = http.post("/api/v1/auth/register", json={
        "name": "Bob",
        "email": "bob@example.com",
        "password": "Sup3rSecret!",
    })
    assert register.status_code == 201
    headers = {"Authorization": f"Bearer {register.json()['access_token']}"}
    me = http.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    body = me.json()
    assert body["role"]["role"] == "attendee"
    assert body["email"] == "bob@example.com"
    assert body["name"] == "Bob"


def test_register_short_password_rejected(http, attendee_role):
    response = http.post("/api/v1/auth/register", json={
        "name": "Short",
        "email": "short@example.com",
        "password": "1234",
    })
    assert response.status_code == 422


def test_register_duplicate_email_returns_409(http, attendee_role):
    payload = {"name": "Dup", "email": "dup@example.com", "password": "Sup3rSecret!"}
    first = http.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    second = http.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409
