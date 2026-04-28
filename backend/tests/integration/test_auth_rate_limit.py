"""Rate-limit smoke test for /auth/login.

The default limit is 5/minute. We fire 6 rapid requests and assert the 6th
returns 429 with the expected JSON error shape.
"""
from .conftest import ADMIN_EMAIL, ADMIN_PASSWORD


def test_login_rate_limit_returns_429_after_5_attempts(http, admin_user):
    for _ in range(5):
        r = http.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        assert r.status_code == 200, r.text

    r = http.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 429, r.text
    body = r.json()
    assert body["code"] == "RateLimitExceeded"
    assert "5 per 1 minute" in body["message"]
