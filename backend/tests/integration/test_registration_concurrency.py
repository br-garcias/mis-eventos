"""Concurrency stress test for spot reservation.

Creates N users upfront, then spawns threads that all attempt to register
to the same published event with capacity N. Verifies that exactly N succeed
and the rest get 409, and that the final confirmed count never exceeds capacity.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from apps.api.rate_limit import limiter


def _event_payload(**overrides):
    default = {
        "name": "Concurrency Test",
        "description": "Race condition test",
        "capacity": 3,
        "start_at": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_at": (datetime.now() + timedelta(days=2)).isoformat(),
        "location": "Bogota",
    }
    default.update(overrides)
    return default


def _create_and_publish_event(http: TestClient, organizer_headers: dict) -> str:
    create = http.post("/api/v1/events", json=_event_payload(), headers=organizer_headers)
    assert create.status_code == 201
    event_id = create.json()["id"]
    pub = http.post(f"/api/v1/events/{event_id}/publish", headers=organizer_headers)
    assert pub.status_code == 204
    return event_id


def _register(http: TestClient, event_id: str, headers: dict) -> int:
    return http.post(f"/api/v1/events/{event_id}/register", headers=headers).status_code


def test_concurrent_registrations_never_overbook(http: TestClient, organizer_headers: dict, attendee_role):
    event_id = _create_and_publish_event(http, organizer_headers)
    capacity = 3
    attempts = 10

    # Create users upfront to avoid race in user creation.
    # The /register endpoint is rate-limited at 5/minute, so we reset
    # the in-memory limiter storage after each batch of 5.
    user_headers = []
    for i in range(attempts):
        if i > 0 and i % 5 == 0:
            if hasattr(limiter, "_storage") and hasattr(limiter._storage, "reset"):
                limiter._storage.reset()
        email = f"conc{i}@{uuid4().hex}.com"
        reg = http.post("/api/v1/auth/register", json={
            "name": f"User {i}",
            "email": email,
            "password": "Sup3rSecret!",
        })
        assert reg.status_code == 201, f"User creation failed: {reg.text}"
        tokens = reg.json()
        user_headers.append({"Authorization": f"Bearer {tokens['access_token']}"})

    results = []
    with ThreadPoolExecutor(max_workers=attempts) as executor:
        futures = [
            executor.submit(_register, http, event_id, h)
            for h in user_headers
        ]
        for future in as_completed(futures):
            results.append(future.result())

    success_count = results.count(201)
    conflict_count = results.count(409)

    assert success_count == capacity
    assert conflict_count == attempts - capacity

    # Verify final event state via GET
    event = http.get(f"/api/v1/events/{event_id}")
    assert event.status_code == 200
    data = event.json()
    assert data["confirmed_attendees"] == capacity
    assert data["available_spots"] == 0
