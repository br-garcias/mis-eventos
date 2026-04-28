from typing import List

from modules.role_views.domain.role_view_dto import RoleView
from modules.role_views.domain.role_view_repository import RoleViewRepository


class RoleLister:
    def __init__(self, view_repository: RoleViewRepository) -> None:
        self._view_repository = view_repository

    def run(self) -> List[RoleView]:
        return self._view_repository.list_all()
