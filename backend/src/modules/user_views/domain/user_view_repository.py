from __future__ import annotations

from abc import ABC, abstractmethod

from modules.user_views.domain.user_view_dto import UserDetailView, UserSummaryView


class UserViewRepository(ABC):
    @abstractmethod
    def search(
        self,
        *,
        email: str | None = None,
        name: str | None = None,
        role_id: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[UserSummaryView], int]: ...

    @abstractmethod
    def find_by_id(self, id: str) -> UserDetailView | None: ...

    @abstractmethod
    def invalidate_cache(self) -> None: ...
