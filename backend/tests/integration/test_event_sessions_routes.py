"""Integration tests for event_sessions bounded context."""
from __future__ import annotations

from datetime import datetime, timedelta


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


def _session_payload(start_offset=timedelta(hours=2), end_offset=timedelta(hours=4), **overrides):
    now = datetime.now() + timedelta(days=1)
    default = {
        "title": "Session One",
        "description": "First session",
        "speaker_name": "Dr. Jane",
        "speaker_bio": "Expert",
        "start_at": (now + start_offset).isoformat(),
        "end_at": (now + end_offset).isoformat(),
        "capacity": 50,
    }
    default.update(overrides)
    return default


# ── CRUD ──────────────────────────────────────────────────────────────────────
def test_create_session_as_organizer(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    payload = _session_payload()
    response = http.post(f"/api/v1/events/{event_id}/sessions", json=payload, headers=organizer_headers)
    assert response.status_code == 201
    assert "id" in response.json()


def test_update_session(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    session = http.post(f"/api/v1/events/{event_id}/sessions", json=_session_payload(), headers=organizer_headers)
    session_id = session.json()["id"]

    patch = http.patch(f"/api/v1/events/{event_id}/sessions/{session_id}", json={
        "title": "Updated Session",
    }, headers=organizer_headers)
    assert patch.status_code == 204


def test_delete_session(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    session = http.post(f"/api/v1/events/{event_id}/sessions", json=_session_payload(), headers=organizer_headers)
    session_id = session.json()["id"]

    delete = http.delete(f"/api/v1/events/{event_id}/sessions/{session_id}", headers=organizer_headers)
    assert delete.status_code == 204

    response = http.get(f"/api/v1/events/{event_id}")
    assert len(response.json()["sessions"]) == 0


# ── Validation guards ─────────────────────────────────────────────────────────
def test_session_outside_event_bounds(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    payload = _session_payload(
        start_offset=timedelta(days=3),
        end_offset=timedelta(days=4),
    )
    response = http.post(f"/api/v1/events/{event_id}/sessions", json=payload, headers=organizer_headers)
    assert response.status_code == 422


def test_session_overlaps(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    event_id = create.json()["id"]
    http.post(f"/api/v1/events/{event_id}/sessions", json=_session_payload(), headers=organizer_headers)
    # overlapping session
    response = http.post(f"/api/v1/events/{event_id}/sessions", json=_session_payload(
        start_offset=timedelta(hours=1), end_offset=timedelta(hours=5)
    ), headers=organizer_headers)
    assert response.status_code == 409


def test_session_capacity_exceeds_event(http, organizer_headers):
    create = http.post("/api/v1/events", json=_event_payload(capacity=50), headers=organizer_headers)
    event_id = create.json()["id"]
    payload = _session_payload(capacity=100)
    response = http.post(f"/api/v1/events/{event_id}/sessions", json=payload, headers=organizer_headers)
    assert response.status_code == 422
