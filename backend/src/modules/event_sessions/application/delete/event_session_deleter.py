from __future__ import annotations

from modules.event_sessions.domain.errors import EventSessionNotFoundError
from modules.event_sessions.domain.event_session_repository import EventSessionRepository
from modules.event_views.application.invalidate_cache.invalidate_event_views_cache import (
    InvalidateEventViewsCache,
)
from modules.shared.domain.value_object.id_value_object import IdValueObject


class EventSessionDeleter:
    def __init__(
        self, repo: EventSessionRepository, cache_invalidator: InvalidateEventViewsCache
    ) -> None:
        self._repo = repo
        self._cache_invalidator = cache_invalidator

    def run(self, *, id: str) -> None:
        session = self._repo.find_by_id(IdValueObject(id))
        if session is None:
            raise EventSessionNotFoundError(id)
        self._repo.delete(IdValueObject(id))
        self._cache_invalidator.invalidate_all()
