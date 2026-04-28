"""Round-trip test for CachedEventViewRepository with fakeredis.

Verifies that DTOs survive JSON serialization/deserialization intact,
including datetime fields — the bug that only surfaced with a real cache backend.
"""
from __future__ import annotations

from datetime import datetime, timezone

import fakeredis
import pytest

from modules.event_views.domain.event_view_dto import EventDetailView, EventSummaryView, Page
from modules.event_views.infrastructure.persistence.cached_event_view_repository import (
    CachedEventViewRepository,
)
from modules.shared.infrastructure.cache.valkey_cache import ValkeyCache


@pytest.fixture
def fake_valkey_cache():
    client = fakeredis.FakeRedis(decode_responses=True)
    return ValkeyCache("valkey://fake", client=client)


class _StubRepository:
    def __init__(self) -> None:
        self.search_calls = 0
        self.find_calls = 0

    def invalidate_cache(self) -> None:
        pass

    def search(self, **kwargs) -> Page[EventSummaryView]:
        self.search_calls += 1
        return Page(
            items=[
                EventSummaryView(
                    id="evt-1",
                    name="Test Event",
                    organizer_id="org-1",
                    status="published",
                    capacity=100,
                    confirmed_attendees=5,
                    available_spots=95,
                    start_at=datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),
                    end_at=datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc),
                    location="Madrid",
                )
            ],
            total=1,
            page=1,
            size=20,
        )

    def find_by_id(self, id: str) -> EventDetailView | None:
        self.find_calls += 1
        return EventDetailView(
            id=id,
            name="Test Event",
            description="A description",
            organizer_id="org-1",
            status="published",
            capacity=100,
            confirmed_attendees=5,
            available_spots=95,
            start_at=datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),
            end_at=datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc),
            location="Madrid",
            created_at=datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 2, 0, 0, tzinfo=timezone.utc),
        )


def test_search_round_trip_through_valkey(fake_valkey_cache):
    inner = _StubRepository()
    cached = CachedEventViewRepository(inner, fake_valkey_cache, ttl_seconds=60)

    first = cached.search()
    assert inner.search_calls == 1
    assert isinstance(first, Page)
    assert isinstance(first.items[0], EventSummaryView)
    assert first.items[0].start_at == datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc)

    second = cached.search()
    assert inner.search_calls == 1  # cache hit
    assert isinstance(second, Page)
    assert isinstance(second.items[0], EventSummaryView)
    assert second.items[0].start_at == datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc)


def test_find_by_id_round_trip_through_valkey(fake_valkey_cache):
    inner = _StubRepository()
    cached = CachedEventViewRepository(inner, fake_valkey_cache, ttl_seconds=60)

    first = cached.find_by_id("evt-1")
    assert inner.find_calls == 1
    assert isinstance(first, EventDetailView)
    assert first.start_at == datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc)
    assert first.created_at == datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)

    second = cached.find_by_id("evt-1")
    assert inner.find_calls == 1  # cache hit
    assert isinstance(second, EventDetailView)
    assert second.start_at == datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc)
    assert second.created_at == datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
