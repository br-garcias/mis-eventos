from modules.event_views.domain.event_view_dto import Page
from modules.shared.domain.query_handler import QueryHandler

from .event_searcher import EventSearcher
from .search_events_query import SearchEventsQuery


class SearchEventsQueryHandler(QueryHandler):
    def __init__(self, searcher: EventSearcher) -> None:
        self._searcher = searcher

    def subscribed_to(self):
        return SearchEventsQuery

    def handle(self, query: SearchEventsQuery) -> Page:
        return self._searcher.run(
            q=query.q,
            status=query.status,
            organizer_id=query.organizer_id,
            date_from=query.date_from,
            date_to=query.date_to,
            sort_by=query.sort_by,
            page=query.page,
            size=query.size,
            user_id=query.user_id,
        )
