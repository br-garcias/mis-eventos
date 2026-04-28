from __future__ import annotations

import logging

from apps.api.config import CACHE_ENABLED
from modules.shared.domain.cache.cache import Cache
from modules.shared.infrastructure.cache.in_memory_cache import InMemoryCache
from modules.shared.infrastructure.cache.null_cache import NullCache

from .shared_di import valkey_client

log = logging.getLogger(__name__)


def _build_cache() -> Cache:
    if not CACHE_ENABLED:
        log.info("CACHE_ENABLED=false — using NullCache")
        return NullCache()

    try:
        from modules.shared.infrastructure.cache.valkey_cache import ValkeyCache

        cache = ValkeyCache("", client=valkey_client)
        if cache.ping():
            return cache
        log.warning("Valkey ping failed — falling back to in-memory cache")
    except Exception as exc:  # noqa: BLE001 - we want any error to fall back
        log.warning("Valkey unavailable (%s) — falling back to in-memory cache", exc)
    return InMemoryCache()


cache: Cache = _build_cache()
