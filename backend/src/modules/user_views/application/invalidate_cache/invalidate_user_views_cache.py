from __future__ import annotations

from modules.user_views.domain.user_view_repository import UserViewRepository


class InvalidateUserViewsCache:
    def __init__(self, repository: UserViewRepository) -> None:
        self._repository = repository

    def invalidate_all(self) -> None:
        self._repository.invalidate_cache()
