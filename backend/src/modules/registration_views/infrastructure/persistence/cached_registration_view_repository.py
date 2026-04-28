from __future__ import annotations

from typing import Any, List

from modules.registration_views.domain.registration_view_repository import (
    RegistrationViewRepository,
)
from modules.registration_views.domain.registration_view_dto import (
    EventAttendeeView,
    MyRegistrationView,
)
from modules.shared.domain.cache.cache import Cache

_PREFIX = "registrations:"


class CachedRegistrationViewRepository(RegistrationViewRepository):
    def __init__(self, inner: RegistrationViewRepository, cache: Cache, ttl_seconds: int = 60) -> None:
        self._inner = inner
        self._cache = cache
        self._ttl = ttl_seconds

    def find_by_user(self, user_id: str) -> List[MyRegistrationView]:
        key = f"{_PREFIX}user:{user_id}"
        cached = self._cache.get(key)
        if cached is not None:
            return [MyRegistrationView.from_primitive(item) for item in cached]

        result = self._inner.find_by_user(user_id)
        self._cache.set(key, [item.to_primitive() for item in result], ttl_seconds=self._ttl)
        return result

    def find_by_event(self, event_id: str) -> List[EventAttendeeView]:
        key = f"{_PREFIX}event:{event_id}"
        cached = self._cache.get(key)
        if cached is not None:
            return [EventAttendeeView.from_primitive(item) for item in cached]

        result = self._inner.find_by_event(event_id)
        self._cache.set(key, [item.to_primitive() for item in result], ttl_seconds=self._ttl)
        return result

    def invalidate_cache(self) -> None:
        self._cache.invalidate_prefix(_PREFIX)
