from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from modules.event_views.domain.event_view_repository import EventViewRepository
from modules.event_views.domain.event_view_dto import EventDetailView, EventSummaryView, Page
from modules.shared.domain.cache.cache import Cache

_PREFIX = "events:"


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _hash_args(parts: dict) -> str:
    payload = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


class CachedEventViewRepository(EventViewRepository):
    def __init__(self, inner: EventViewRepository, cache: Cache, ttl_seconds: int = 60) -> None:
        self._inner = inner
        self._cache = cache
        self._ttl = ttl_seconds

    def invalidate_cache(self) -> None:
        self._cache.invalidate_prefix(_PREFIX)

    def search(
        self,
        *,
        q: str | None = None,
        status: str | None = None,
        organizer_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: str = "start_at",
        page: int = 1,
        size: int = 20,
        user_id: str | None = None,
    ) -> Page[EventSummaryView]:
        key = f"{_PREFIX}search:" + _hash_args({
            "q": q,
            "status": status,
            "organizer_id": organizer_id,
            "date_from": _serialize(date_from),
            "date_to": _serialize(date_to),
            "sort_by": sort_by,
            "page": page,
            "size": size,
            "user_id": user_id,
        })

        cached = self._cache.get(key)
        if cached is not None:
            return Page.from_primitive(cached, item_factory=EventSummaryView.from_primitive)

        result = self._inner.search(
            q=q,
            status=status,
            organizer_id=organizer_id,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            page=page,
            size=size,
            user_id=user_id,
        )
        self._cache.set(key, result.to_primitive(), ttl_seconds=self._ttl)
        return result

    def find_by_id(self, id: str, user_id: str | None = None) -> EventDetailView | None:
        key = f"{_PREFIX}detail:{id}:{user_id}"
        cached = self._cache.get(key)
        if cached is not None:
            return EventDetailView.from_primitive(cached)
        result = self._inner.find_by_id(id, user_id)
        if result is not None:
            self._cache.set(key, result.to_primitive(), ttl_seconds=self._ttl)
        return result

    def find_by_organizer(
        self,
        organizer_id: str,
        q: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> Page[EventSummaryView]:
        key = f"{_PREFIX}organizer:{organizer_id}:" + _hash_args({
            "q": q,
            "status": status,
            "page": page,
            "size": size,
        })
        cached = self._cache.get(key)
        if cached is not None:
            return Page.from_primitive(cached, item_factory=EventSummaryView.from_primitive)

        result = self._inner.find_by_organizer(
            organizer_id=organizer_id,
            q=q,
            status=status,
            page=page,
            size=size,
        )
        self._cache.set(key, result.to_primitive(), ttl_seconds=self._ttl)
        return result
