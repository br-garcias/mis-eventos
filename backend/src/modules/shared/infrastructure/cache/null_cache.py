from __future__ import annotations

from typing import Any

from modules.shared.domain.cache.cache import Cache


class NullCache(Cache):
    def get(self, key: str) -> Any | None:
        return None

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        return None

    def delete(self, key: str) -> None:
        return None

    def invalidate_prefix(self, prefix: str) -> None:
        return None

    def clear(self) -> None:
        return None
