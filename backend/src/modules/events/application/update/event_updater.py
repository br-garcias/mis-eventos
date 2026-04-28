from __future__ import annotations

from datetime import datetime

from modules.event_views.application.invalidate_cache.invalidate_event_views_cache import (
    InvalidateEventViewsCache,
)
from modules.events.application.authorization import load_event_for_actor
from modules.events.domain.event_repository import EventRepository


class EventUpdater:
    def __init__(self, repo: EventRepository, cache_invalidator: InvalidateEventViewsCache) -> None:
        self._repo = repo
        self._cache_invalidator = cache_invalidator

    def run(
        self,
        *,
        id: str,
        actor_user_id: str,
        actor_role: str,
        name: str | None,
        description: str | None,
        location: str | None,
        start_at: datetime | None,
        end_at: datetime | None,
        capacity: int | None,
    ) -> None:
        event = load_event_for_actor(
            self._repo, event_id=id, actor_user_id=actor_user_id, actor_role=actor_role
        )

        if any(v is not None for v in (name, description, location)):
            event.update_details(name=name, description=description, location=location)

        if start_at is not None or end_at is not None:
            new_start = start_at or event.dates.start_at
            new_end = end_at or event.dates.end_at
            event.reschedule(start_at=new_start, end_at=new_end)

        if capacity is not None:
            event.change_capacity(capacity)

        self._repo.save(event)
        self._cache_invalidator.invalidate_all()
