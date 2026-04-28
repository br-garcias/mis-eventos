from modules.event_views.domain.event_view_dto import EventDetailView
from modules.shared.domain.query_handler import QueryHandler

from .event_finder_by_id import EventFinderById
from .find_event_by_id_query import FindEventByIdQuery


class FindEventByIdQueryHandler(QueryHandler):
    def __init__(self, finder: EventFinderById) -> None:
        self._finder = finder

    def subscribed_to(self):
        return FindEventByIdQuery

    def handle(self, query: FindEventByIdQuery) -> EventDetailView | None:
        return self._finder.run(query.id, user_id=query.user_id)
