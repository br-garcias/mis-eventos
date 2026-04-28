from __future__ import annotations

from typing import List

from modules.shared.domain.cache.cache import Cache
from modules.user_views.domain.user_view_dto import UserDetailView, UserSummaryView
from modules.user_views.domain.user_view_repository import UserViewRepository

_PREFIX = "users:"


class CachedUserViewRepository(UserViewRepository):
    def __init__(self, inner: UserViewRepository, cache: Cache, ttl_seconds: int = 60) -> None:
        self._inner = inner
        self._cache = cache
        self._ttl = ttl_seconds

    def invalidate_cache(self) -> None:
        self._cache.invalidate_prefix(_PREFIX)

    def search(
        self,
        *,
        email: str | None = None,
        name: str | None = None,
        role_id: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[UserSummaryView], int]:
        key = f"{_PREFIX}search:email={email}:name={name}:role={role_id}:page={page}:size={size}"
        cached = self._cache.get(key)
        if cached is not None:
            items = [UserSummaryView.from_primitive(item) for item in cached["items"]]
            return items, cached["total"]

        items, total = self._inner.search(
            email=email, name=name, role_id=role_id, page=page, size=size
        )
        self._cache.set(
            key,
            {"items": [item.to_primitive() for item in items], "total": total},
            ttl_seconds=self._ttl,
        )
        return items, total

    def find_by_id(self, id: str) -> UserDetailView | None:
        key = f"{_PREFIX}id:{id}"
        cached = self._cache.get(key)
        if cached is not None:
            return UserDetailView.from_primitive(cached)

        result = self._inner.find_by_id(id)
        if result is not None:
            self._cache.set(key, result.to_primitive(), ttl_seconds=self._ttl)
        return result
