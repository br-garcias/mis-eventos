from typing import List

from modules.role_views.domain.role_view_dto import RoleView
from modules.shared.domain.query_handler import QueryHandler

from .list_roles_query import ListRolesQuery
from .role_lister import RoleLister


class ListRolesQueryHandler(QueryHandler):
    def __init__(self, lister: RoleLister) -> None:
        self._lister = lister

    def subscribed_to(self):
        return ListRolesQuery

    def handle(self, query: ListRolesQuery) -> List[RoleView]:
        return self._lister.run()
