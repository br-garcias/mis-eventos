from datetime import datetime

from modules.event_views.domain.event_view_repository import EventViewRepository
from modules.event_views.domain.event_view_dto import EventSummaryView, Page


class EventSearcher:
    def __init__(self, view_repository: EventViewRepository) -> None:
        self._view_repository = view_repository

    def run(
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
    ) -> Page[EventSummaryView]:
        return self._view_repository.search(
            q=q,
            status=status,
            organizer_id=organizer_id,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            page=page,
            size=size,
            user_id=user_id,
        )
