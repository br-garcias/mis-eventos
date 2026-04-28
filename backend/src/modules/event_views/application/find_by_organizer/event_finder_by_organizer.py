from modules.event_views.domain.event_view_dto import Page
from modules.event_views.domain.event_view_repository import EventViewRepository


class EventFinderByOrganizer:
    def __init__(self, repository: EventViewRepository) -> None:
        self._repository = repository

    def run(
        self,
        organizer_id: str,
        q: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> Page:
        return self._repository.find_by_organizer(
            organizer_id=organizer_id,
            q=q,
            status=status,
            page=page,
            size=size,
        )
