from __future__ import annotations

import json
import logging
from typing import Any

from modules.shared.domain.cache.cache import Cache

log = logging.getLogger(__name__)


class ValkeyCache(Cache):
    def __init__(self, url: str, *, prefix: str = "demo:", client=None) -> None:
        try:
            import redis
        except ImportError as exc:
            raise RuntimeError("redis package is required for ValkeyCache") from exc

        self._client = client if client is not None else redis.Redis.from_url(url, decode_responses=True)
        self._prefix = prefix

    # ── Cache protocol ────────────────────────────────────────────────────────
    def get(self, key: str) -> Any | None:
        raw = self._client.get(self._k(key))
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        payload = json.dumps(value, default=str)
        if ttl_seconds is None or ttl_seconds <= 0:
            self._client.set(self._k(key), payload)
        else:
            self._client.set(self._k(key), payload, ex=ttl_seconds)

    def delete(self, key: str) -> None:
        self._client.delete(self._k(key))

    def invalidate_prefix(self, prefix: str) -> None:
        match = self._k(prefix) + "*"
        for key in self._client.scan_iter(match=match, count=500):
            self._client.unlink(key)

    def clear(self) -> None:
        self.invalidate_prefix("")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _k(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception:  # pragma: no cover - network specific
            return False
