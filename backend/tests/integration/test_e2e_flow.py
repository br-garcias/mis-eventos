"""End-to-end smoke test covering the full happy path.

register → login → create event (organizer) → publish → register attendee
→ view registrations → cancel registration
"""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient


def test_e2e_full_lifecycle(http: TestClient, organizer_headers: dict, attendee_headers: dict):
    # 1. Organizer creates an event
    event_payload = {
        "name": "E2E Test Conference",
        "description": "A full lifecycle test",
        "capacity": 10,
        "start_at": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_at": (datetime.now() + timedelta(days=2)).isoformat(),
        "location": "Bogota",
    }
    create = http.post("/api/v1/events", json=event_payload, headers=organizer_headers)
    assert create.status_code == 201
    event_id = create.json()["id"]

    # 2. Publish the event
    pub = http.post(f"/api/v1/events/{event_id}/publish", headers=organizer_headers)
    assert pub.status_code == 204

    # 3. Attendee registers
    reg = http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert reg.status_code == 201
    registration_id = reg.json()["id"]

    # 4. Attendee lists their registrations
    my = http.get("/api/v1/me/registrations", headers=attendee_headers)
    assert my.status_code == 200
    registrations = my.json()
    assert len(registrations) == 1
    assert registrations[0]["event_id"] == event_id

    # 5. Organizer lists attendees
    attendees = http.get(f"/api/v1/events/{event_id}/attendees", headers=organizer_headers)
    assert attendees.status_code == 200
    attendee_list = attendees.json()
    assert len(attendee_list) == 1

    # 6. Attendee cancels registration
    cancel = http.delete(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert cancel.status_code == 204

    # 7. Spot released, can re-register
    re_reg = http.post(f"/api/v1/events/{event_id}/register", headers=attendee_headers)
    assert re_reg.status_code == 201

    # 8. Final event state
    event = http.get(f"/api/v1/events/{event_id}")
    assert event.status_code == 200
    data = event.json()
    assert data["confirmed_attendees"] == 1
    assert data["available_spots"] == 9
