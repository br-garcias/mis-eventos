"""Integration tests for registrations bounded context."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient


def _event_payload(**overrides):
    default = {
        "name": "Test Event",
        "description": "A great event",
        "capacity": 5,
        "start_at": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_at": (datetime.now() + timedelta(days=2)).isoformat(),
        "location": "Bogota",
    }
    default.update(overrides)
    return default


def _create_and_publish_event(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    assert create.status_code == 201
    event_id = create.json()["id"]
    pub = http.post(f"/api/v1/events/{event_id}/publish", headers=organizer_headers)
    assert pub.status_code == 204
    return event_id


# ── Register ────────────────────────────────────────────────────────────────────
def test_register_to_published_event(http, organizer_headers, attendee_headers):
    event_id = _create_and_publish_event(http, organizer_headers)
    reg = http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert reg.status_code == 201
    assert "id" in reg.json()


def test_register_to_draft_event_fails(http, organizer_headers, attendee_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    reg = http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert reg.status_code == 409


def test_double_registration_fails(http, organizer_headers, attendee_headers):
    event_id = _create_and_publish_event(http, organizer_headers)
    first = http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert first.status_code == 201
    second = http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert second.status_code == 409


def test_register_full_event_fails(http, organizer_headers, attendee_headers):
    event_id = _create_and_publish_event(http, organizer_headers)
    # Fill capacity (5)
    for i in range(5):
        # Create temp attendee users via public registration for extra slots
        extra = f"extra{i}@example.com"
        r = http.post("/api/v1/auth/register", json={
            "name": f"Extra {i}",
            "email": extra,
            "password": "Sup3rSecret!",
        })
        assert r.status_code == 201
        tokens = r.json()
        h = {"Authorization": f"Bearer {tokens['access_token']}"}
        reg = http.post(f"/api/v1/events/{event_id}/register", headers=h)
        assert reg.status_code == 201, f"Failed at slot {i}: {reg.text}"

    # 6th should fail
    full = http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert full.status_code == 409


# ── Cancel ─────────────────────────────────────────────────────────────────────
def test_cancel_registration(http, organizer_headers, attendee_headers):
    event_id = _create_and_publish_event(http, organizer_headers)
    reg = http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert reg.status_code == 201

    cancel = http.delete(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert cancel.status_code == 204

    # Spot is released, can register again
    re_reg = http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert re_reg.status_code == 201


# ── List ───────────────────────────────────────────────────────────────────────
def test_list_my_registrations(http, organizer_headers, attendee_headers):
    event_id = _create_and_publish_event(http, organizer_headers)
    http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)

    my = http.get("/api/v1/me/registrations", headers=attendee_headers)
    assert my.status_code == 200
    assert len(my.json()) == 1
    assert my.json()[0]["event"]["id"] == event_id


def test_list_event_attendees_as_organizer(http, organizer_headers, attendee_headers):
    event_id = _create_and_publish_event(http, organizer_headers)
    http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)

    attendees = http.get(f"/api/v1/events/{event_id}/attendees", headers=organizer_headers)
    assert attendees.status_code == 200
    assert len(attendees.json()) == 1


def test_list_event_attendees_as_attendee_forbidden(http, organizer_headers, attendee_headers):
    event_id = _create_and_publish_event(http, organizer_headers)
    attendees = http.get(f"/api/v1/events/{event_id}/attendees", headers=attendee_headers)
    assert attendees.status_code == 403
