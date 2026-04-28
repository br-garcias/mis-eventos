from __future__ import annotations

from modules.event_views.application.invalidate_cache.invalidate_event_views_cache import (
    InvalidateEventViewsCache,
)
from modules.events.application.authorization import load_event_for_actor
from modules.events.domain.event_repository import EventRepository


class EventCanceller:
    def __init__(self, repo: EventRepository, cache_invalidator: InvalidateEventViewsCache) -> None:
        self._repo = repo
        self._cache_invalidator = cache_invalidator

    def run(self, *, id: str, actor_user_id: str, actor_role: str) -> None:
        event = load_event_for_actor(
            self._repo, event_id=id, actor_user_id=actor_user_id, actor_role=actor_role
        )
        event.cancel()
        self._repo.save(event)
        self._cache_invalidator.invalidate_all()
