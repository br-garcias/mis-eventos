from __future__ import annotations

from typing import List

from modules.shared.domain.cache.cache import Cache
from modules.role_views.domain.role_view_dto import RoleView
from modules.role_views.domain.role_view_repository import RoleViewRepository

_PREFIX = "roles:"


class CachedRoleViewRepository(RoleViewRepository):
    def __init__(self, inner: RoleViewRepository, cache: Cache, ttl_seconds: int = 60) -> None:
        self._inner = inner
        self._cache = cache
        self._ttl = ttl_seconds

    def invalidate_cache(self) -> None:
        self._cache.invalidate_prefix(_PREFIX)

    def list_all(self) -> List[RoleView]:
        key = f"{_PREFIX}list"
        cached = self._cache.get(key)
        if cached is not None:
            return [RoleView.from_primitive(item) for item in cached]

        result = self._inner.list_all()
        self._cache.set(
            key,
            [item.to_primitive() for item in result],
            ttl_seconds=self._ttl,
        )
        return result
