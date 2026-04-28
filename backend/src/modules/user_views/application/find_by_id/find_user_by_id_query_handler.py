from modules.shared.domain.query_handler import QueryHandler
from modules.user_views.domain.user_view_dto import UserDetailView

from .find_user_by_id_query import FindUserByIdQuery
from .user_finder_by_id import UserFinderById


class FindUserByIdQueryHandler(QueryHandler):
    def __init__(self, finder: UserFinderById) -> None:
        self._finder = finder

    def subscribed_to(self):
        return FindUserByIdQuery

    def handle(self, query: FindUserByIdQuery) -> UserDetailView | None:
        return self._finder.run(query.id)