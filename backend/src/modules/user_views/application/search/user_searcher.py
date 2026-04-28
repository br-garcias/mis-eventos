from modules.user_views.domain.user_view_dto import UserSummaryView
from modules.user_views.domain.user_view_repository import UserViewRepository


class UserSearcher:
    def __init__(self, view_repository: UserViewRepository) -> None:
        self._view_repository = view_repository

    def run(
        self,
        *,
        email: str | None = None,
        name: str | None = None,
        role_id: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[UserSummaryView], int]:
        return self._view_repository.search(
            email=email, name=name, role_id=role_id, page=page, size=size
        )
