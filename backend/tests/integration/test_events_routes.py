"""Integration tests for the events bounded context."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from .conftest import ADMIN_EMAIL, ADMIN_PASSWORD


# ── Helpers ───────────────────────────────────────────────────────────────────
def _event_payload(**overrides):
    default = {
        "name": "Test Event",
        "description": "A great event",
        "capacity": 100,
        "start_at": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_at": (datetime.now() + timedelta(days=2)).isoformat(),
        "location": "Bogota",
    }
    default.update(overrides)
    return default


# ── Public reads ──────────────────────────────────────────────────────────────
def test_list_events_empty(http):
    response = http.get("/api/v1/events")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_get_event_not_found(http):
    response = http.get("/api/v1/events/nonexistent")
    assert response.status_code == 404


# ── Create ────────────────────────────────────────────────────────────────────
def test_create_event_as_organizer(http, organizer_headers):
    payload = _event_payload()
    response = http.post("/api/v1/events", json=payload, headers=organizer_headers)
    assert response.status_code == 201
    assert "id" in response.json()


def test_create_event_unauthenticated(http):
    response = http.post("/api/v1/events", json=_event_payload())
    assert response.status_code == 401


def test_create_event_as_attendee(http, attendee_role):
    # create an attendee user and try to create an event
    from uuid import uuid4
    from apps.api.di.shared_di import password_hasher
    from apps.api.di.users_di import user_repository
    from modules.users.domain.user import User

    user = User.create(
        id=str(uuid4()),
        name="Attendee Joe",
        email="attendee@example.com",
        password_hash=password_hasher.hash("Sup3rSecret!"),
        role_id=attendee_role.id.value,
    )
    user_repository.save(user)

    login = http.post("/api/v1/auth/login", json={
        "email": "attendee@example.com",
        "password": "Sup3rSecret!",
    })
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = http.post("/api/v1/events", json=_event_payload(), headers=headers)
    assert response.status_code == 403


# ── Update / lifecycle ────────────────────────────────────────────────────────
def test_publish_and_read_event(http, organizer_headers, organizer_user):
    # create
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]

    # list as draft
    list_resp = http.get("/api/v1/events")
    assert list_resp.status_code == 200
    assert len(list_resp.json()["items"]) == 1

    # publish
    pub = http.post(f"/api/v1/events/{event_id}/publish", headers=organizer_headers)
    assert pub.status_code == 204

    # read
    get = http.get(f"/api/v1/events/{event_id}")
    assert get.status_code == 200
    body = get.json()
    assert body["status"] == "published"
    assert "organizer" in body
    assert body["organizer"]["id"] == organizer_user.id.value
    assert "name" in body["organizer"]
    assert "email" in body["organizer"]
    assert "sessions" in body
    assert isinstance(body["sessions"], list)


def test_cancel_event(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    cancel = http.post(f"/api/v1/events/{event_id}/cancel", headers=organizer_headers)
    assert cancel.status_code == 204
    get = http.get(f"/api/v1/events/{event_id}")
    assert get.json()["status"] == "cancelled"


def test_update_event(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    patch = http.patch(f"/api/v1/events/{event_id}", json={"name": "Updated Name"}, headers=organizer_headers)
    assert patch.status_code == 204
    get = http.get(f"/api/v1/events/{event_id}")
    assert get.json()["name"] == "Updated Name"


def test_delete_event(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    delete = http.delete(f"/api/v1/events/{event_id}", headers=organizer_headers)
    assert delete.status_code == 204
    get = http.get(f"/api/v1/events/{event_id}")
    assert get.status_code == 404


# ── Status transition guards ──────────────────────────────────────────────────
def test_publish_non_draft_returns_409(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    http.post(f"/api/v1/events/{event_id}/publish", headers=organizer_headers)
    second = http.post(f"/api/v1/events/{event_id}/publish", headers=organizer_headers)
    assert second.status_code == 409


def test_cancel_finished_returns_409(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    http.post(f"/api/v1/events/{event_id}/publish", headers=organizer_headers)
    # mark ongoing then finished (simulated via direct repository)
    from apps.api.di.events_di import event_repository
    from modules.events.domain.event_status import EventStatus
    from modules.shared.domain.value_object.id_value_object import IdValueObject
    event = event_repository.find_by_id(IdValueObject(event_id))
    event.mark_ongoing()
    event.finish()
    event_repository.save(event)
    cancel = http.post(f"/api/v1/events/{event_id}/cancel", headers=organizer_headers)
    assert cancel.status_code == 409


# (Ownership guards tested via unit tests; integration omitted for brevity.)


# ── Search / pagination ───────────────────────────────────────────────────────
def test_search_events_by_name(http, organizer_headers):
    http.post("/api/v1/events", json=_event_payload(name="Python Conf"), headers=organizer_headers)
    http.post("/api/v1/events", json=_event_payload(name="JS Meetup"), headers=organizer_headers)

    search = http.get("/api/v1/events?q=Python")
    assert search.status_code == 200
    names = [e["name"] for e in search.json()["items"]]
    assert "Python Conf" in names


def test_filter_by_status(http, organizer_headers):
    c1 = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    c2 = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    http.post(f"/api/v1/events/{c2.json()['id']}/publish", headers=organizer_headers)

    published = http.get("/api/v1/events?status=published")
    assert published.status_code == 200
    assert len(published.json()["items"]) == 1


# ── Validation guards ─────────────────────────────────────────────────────────
def test_create_event_zero_capacity_returns_422(http, organizer_headers):
    response = http.post("/api/v1/events", json=_event_payload(capacity=0), headers=organizer_headers)
    assert response.status_code == 422


def test_create_event_invalid_dates_returns_422(http, organizer_headers):
    start = datetime.now()
    end = start - timedelta(days=1)
    response = http.post("/api/v1/events", json=_event_payload(start_at=start.isoformat(), end_at=end.isoformat()), headers=organizer_headers)
    assert response.status_code == 422


# ── My events (organizer) ───────────────────────────────────────────────────────
def test_list_my_events_empty(http, organizer_headers):
    response = http.get("/api/v1/events/me/list", headers=organizer_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_list_my_events_with_events(http, organizer_headers):
    http.post("/api/v1/events", json=_event_payload(name="My Event 1"), headers=organizer_headers)
    http.post("/api/v1/events", json=_event_payload(name="My Event 2"), headers=organizer_headers)

    response = http.get("/api/v1/events/me/list", headers=organizer_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    names = [e["name"] for e in body["items"]]
    assert "My Event 1" in names
    assert "My Event 2" in names


def test_list_my_events_filter_by_name(http, organizer_headers):
    http.post("/api/v1/events", json=_event_payload(name="Python Conf"), headers=organizer_headers)
    http.post("/api/v1/events", json=_event_payload(name="JS Meetup"), headers=organizer_headers)

    response = http.get("/api/v1/events/me/list?q=python", headers=organizer_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Python Conf"


def test_list_my_events_filter_by_status(http, organizer_headers):
    e1 = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    e2 = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    http.post(f"/api/v1/events/{e2.json()['id']}/publish", headers=organizer_headers)

    response = http.get("/api/v1/events/me/list?status=published", headers=organizer_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "published"


def test_list_my_events_unauthenticated(http):
    response = http.get("/api/v1/events/me/list")
    assert response.status_code == 401
