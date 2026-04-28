from modules.user_views.domain.user_view_dto import UserDetailView
from modules.user_views.domain.user_view_repository import UserViewRepository


class UserFinderById:
    def __init__(self, view_repository: UserViewRepository) -> None:
        self._view_repository = view_repository

    def run(self, id: str) -> UserDetailView | None:
        return self._view_repository.find_by_id(id)
