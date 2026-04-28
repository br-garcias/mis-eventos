from modules.event_views.domain.event_view_dto import Page
from modules.shared.domain.query_handler import QueryHandler

from .search_users_query import SearchUsersQuery
from .user_searcher import UserSearcher


class SearchUsersQueryHandler(QueryHandler):
    def __init__(self, searcher: UserSearcher) -> None:
        self._searcher = searcher

    def subscribed_to(self):
        return SearchUsersQuery

    def handle(self, query: SearchUsersQuery) -> Page:
        items, total = self._searcher.run(
            email=query.email,
            name=query.name,
            role_id=query.role_id,
            page=query.page,
            size=query.size,
        )
        return Page(items=items, total=total, page=query.page, size=query.size)
