from modules.event_views.domain.event_view_dto import Page
from modules.shared.domain.query_handler import QueryHandler

from .event_finder_by_organizer import EventFinderByOrganizer
from .find_my_events_query import FindMyEventsQuery


class FindMyEventsQueryHandler(QueryHandler):
    def __init__(self, finder: EventFinderByOrganizer) -> None:
        self._finder = finder

    def subscribed_to(self):
        return FindMyEventsQuery

    def handle(self, query: FindMyEventsQuery) -> Page:
        return self._finder.run(
            organizer_id=query.organizer_id,
            q=query.q,
            status=query.status,
            page=query.page,
            size=query.size,
        )
