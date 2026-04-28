from __future__ import annotations

from datetime import datetime

from modules.event_views.application.invalidate_cache.invalidate_event_views_cache import (
    InvalidateEventViewsCache,
)
from modules.events.domain.event import Event
from modules.events.domain.event_repository import EventRepository


class EventCreator:
    def __init__(
        self, repo: EventRepository, cache_invalidator: InvalidateEventViewsCache
    ) -> None:
        self._repo = repo
        self._cache_invalidator = cache_invalidator

    def run(
        self,
        *,
        id: str,
        name: str,
        description: str,
        organizer_id: str,
        capacity: int,
        start_at: datetime,
        end_at: datetime,
        location: str,
    ) -> None:
        event = Event.create(
            id=id,
            name=name,
            description=description,
            organizer_id=organizer_id,
            capacity=capacity,
            start_at=start_at,
            end_at=end_at,
            location=location,
        )
        self._repo.save(event)
        self._cache_invalidator.invalidate_all()
