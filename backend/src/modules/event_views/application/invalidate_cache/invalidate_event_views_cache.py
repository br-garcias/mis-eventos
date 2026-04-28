from __future__ import annotations

from modules.event_views.domain.event_view_repository import EventViewRepository


class InvalidateEventViewsCache:
    def __init__(self, repository: EventViewRepository) -> None:
        self._repository = repository

    def invalidate_all(self) -> None:
        self._repository.invalidate_cache()
