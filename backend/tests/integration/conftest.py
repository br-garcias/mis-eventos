"""Integration test scaffolding.

Strategy: monkey-patch the Mongo driver with `mongomock` BEFORE the DI module
is imported. After that, the whole app boots normally end-to-end against an
in-memory Mongo replacement.
"""
from __future__ import annotations

import os
from uuid import uuid4

import fakeredis
import mongomock
import pytest
from fastapi.testclient import TestClient


# ── Test environment defaults (must be set before any module reads them) ──────
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ISSUER", "https://test.local")
os.environ.setdefault("MONGO_DATABASE", "demo_test")
os.environ.setdefault("VALKEY_URL", "redis://localhost:6379/0")


@pytest.fixture(scope="session", autouse=True)
def _patch_mongo_driver():
    """Replace pymongo.MongoClient with a single shared mongomock instance."""
    # Pass an URL so mongomock parses the default database name (used by .get_database()).
    fake = mongomock.MongoClient("mongodb://localhost:27017/demo_test")

    import modules.shared.infrastructure.persistence.mongo.mongo_client_factory as mcf
    original = mcf.MongoClient
    mcf.MongoClient = lambda *_args, **_kwargs: fake  # type: ignore[assignment]

    # Reset any clients cached before patching
    mcf.MongoClientFactory._clients.clear()

    yield fake

    mcf.MongoClient = original  # type: ignore[assignment]
    mcf.MongoClientFactory._clients.clear()


@pytest.fixture(scope="session", autouse=True)
def _patch_valkey_client():
    """Replace redis.Redis in shared DI with a shared fakeredis instance."""
    import redis
    import apps.api.di.shared_di as shared_di
    import apps.api.di.auth_di as auth_di

    fake = fakeredis.FakeRedis(decode_responses=True)
    original = shared_di.valkey_client
    shared_di.valkey_client = fake

    # Re-build the session repository and services with the fake client
    from modules.auth.infrastructure.persistence.valkey_session_repository import (
        ValkeySessionRepository,
    )
    from modules.auth.application.sessions.session_creator import SessionCreator
    from modules.auth.application.sessions.session_revoker import SessionRevoker
    from datetime import timedelta

    auth_di._session_repository = ValkeySessionRepository(fake)
    auth_di._session_creator = SessionCreator(
        auth_di._session_repository,
        refresh_ttl=timedelta(seconds=auth_di.JWT_REFRESH_TTL),
    )
    auth_di._session_revoker = SessionRevoker(auth_di._session_repository)

    yield fake

    shared_di.valkey_client = original


@pytest.fixture(scope="session")
def app(_patch_mongo_driver, _patch_valkey_client):
    from apps.api.app import app as fastapi_app
    return fastapi_app


@pytest.fixture(scope="session")
def http(app) -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Clear slowapi in-memory counters so each test starts with a clean slate."""
    from apps.api.rate_limit import limiter

    if hasattr(limiter, "_storage") and hasattr(limiter._storage, "reset"):
        limiter._storage.reset()
    yield


@pytest.fixture(autouse=True)
def _reset_db(_patch_mongo_driver):
    """Wipe every collection between tests so each test starts clean."""
    for db_name in _patch_mongo_driver.list_database_names():
        db = _patch_mongo_driver[db_name]
        for col in db.list_collection_names():
            db[col].delete_many({})
    yield


@pytest.fixture(autouse=True)
def _reset_valkey(_patch_valkey_client):
    """Flush all keys in the fake Valkey between tests."""
    _patch_valkey_client.flushall()
    yield


# ── Domain helpers ────────────────────────────────────────────────────────────
ADMIN_PASSWORD = "Sup3rSecret!"
ADMIN_EMAIL = "admin@example.com"


@pytest.fixture
def admin_role():
    from apps.api.di.roles_di import role_repository
    from modules.roles.domain.role import Role
    role = Role.create(id=str(uuid4()), name="admin")
    role_repository.save(role)  # type: ignore[attr-defined]
    return role


@pytest.fixture
def admin_user(admin_role):
    from apps.api.di.shared_di import password_hasher
    from apps.api.di.users_di import user_repository
    from modules.users.domain.user import User
    user = User.create(
        id=str(uuid4()),
        name="Root Admin",
        email=ADMIN_EMAIL,
        password_hash=password_hasher.hash(ADMIN_PASSWORD),
        role_id=admin_role.id.value,
    )
    user_repository.save(user)
    return user


@pytest.fixture
def admin_tokens(http: TestClient, admin_user) -> dict:
    response = http.post("/api/v1/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
    })
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def admin_headers(admin_tokens) -> dict:
    return {"Authorization": f"Bearer {admin_tokens['access_token']}"}


@pytest.fixture
def attendee_role():
    from apps.api.di.roles_di import role_repository
    from modules.roles.domain.role import Role
    from modules.roles.domain.role_name import RoleName
    role = Role.create(id=str(uuid4()), name=RoleName.ATTENDEE.value)
    role_repository.save(role)  # type: ignore[attr-defined]
    return role


@pytest.fixture
def organizer_role():
    from apps.api.di.roles_di import role_repository
    from modules.roles.domain.role import Role
    from modules.roles.domain.role_name import RoleName
    role = Role.create(id=str(uuid4()), name=RoleName.ORGANIZER.value)
    role_repository.save(role)  # type: ignore[attr-defined]
    return role


@pytest.fixture
def organizer_user(organizer_role):
    from uuid import uuid4
    from apps.api.di.shared_di import password_hasher
    from apps.api.di.users_di import user_repository
    from modules.users.domain.user import User
    user = User.create(
        id=str(uuid4()),
        name="Event Organizer",
        email="organizer@example.com",
        password_hash=password_hasher.hash("Sup3rSecret!"),
        role_id=organizer_role.id.value,
    )
    user_repository.save(user)
    return user


@pytest.fixture
def organizer_tokens(http: TestClient, organizer_user) -> dict:
    response = http.post("/api/v1/auth/login", json={
        "email": "organizer@example.com",
        "password": "Sup3rSecret!",
    })
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def organizer_headers(organizer_tokens) -> dict:
    return {"Authorization": f"Bearer {organizer_tokens['access_token']}"}


@pytest.fixture
def attendee_user(attendee_role):
    from uuid import uuid4
    from apps.api.di.shared_di import password_hasher
    from apps.api.di.users_di import user_repository
    from modules.users.domain.user import User
    user = User.create(
        id=str(uuid4()),
        name="Event Attendee",
        email="attendee@example.com",
        password_hash=password_hasher.hash("Sup3rSecret!"),
        role_id=attendee_role.id.value,
    )
    user_repository.save(user)
    return user


@pytest.fixture
def attendee_tokens(http: TestClient, attendee_user) -> dict:
    response = http.post("/api/v1/auth/login", json={
        "email": "attendee@example.com",
        "password": "Sup3rSecret!",
    })
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def attendee_headers(attendee_tokens) -> dict:
    return {"Authorization": f"Bearer {attendee_tokens['access_token']}"}
