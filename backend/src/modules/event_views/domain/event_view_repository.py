from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from .event_view_dto import EventDetailView, EventSummaryView, Page


class EventViewRepository(ABC):
    @abstractmethod
    def search(
        self,
        *,
        q: str | None = None,
        status: str | None = None,
        organizer_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: str = "start_at",
        page: int = 1,
        size: int = 20,
        user_id: str | None = None,
    ) -> Page[EventSummaryView]: ...

    @abstractmethod
    def find_by_id(self, id: str, user_id: str | None = None) -> EventDetailView | None: ...

    @abstractmethod
    def find_by_organizer(
        self,
        organizer_id: str,
        q: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> Page[EventSummaryView]: ...

    @abstractmethod
    def invalidate_cache(self) -> None: ...
