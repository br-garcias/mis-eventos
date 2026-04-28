from modules.event_views.domain.event_view_repository import EventViewRepository
from modules.event_views.domain.event_view_dto import EventDetailView


class EventFinderById:
    def __init__(self, view_repository: EventViewRepository) -> None:
        self._view_repository = view_repository

    def run(self, id: str, user_id: str | None = None) -> EventDetailView | None:
        return self._view_repository.find_by_id(id, user_id=user_id)
