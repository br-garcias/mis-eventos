from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache

try:
    from dotenv import load_dotenv

    load_dotenv(override=False)
except Exception:
    pass


def _env(key: str, default: str | None = None) -> str | None:
    val = os.getenv(key)
    if val is None or val == "":
        return default
    return val


def _env_int(key: str, default: int) -> int:
    raw = _env(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_bool(key: str, default: bool) -> bool:
    raw = _env(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_list(key: str, default: list[str]) -> list[str]:
    raw = _env(key)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class JwtSettings:
    secret: str = field(default_factory=lambda: _env("JWT_SECRET", "dev-secret-change-in-production"))
    issuer: str = field(default_factory=lambda: _env("JWT_ISSUER", "https://api.demo.io"))
    access_ttl_seconds: int = field(default_factory=lambda: _env_int("JWT_ACCESS_TTL", 900))
    refresh_ttl_seconds: int = field(default_factory=lambda: _env_int("JWT_REFRESH_TTL", 2_592_000))


@dataclass(frozen=True)
class MongoSettings:
    url: str = field(default_factory=lambda: _env("MONGO_URL", "mongodb://localhost:27017"))


@dataclass(frozen=True)
class CacheSettings:
    valkey_url: str = field(default_factory=lambda: _env("VALKEY_URL", "redis://localhost:6379/0"))
    ttl_seconds: int = field(default_factory=lambda: _env_int("CACHE_TTL_SECONDS", 60))
    enabled: bool = field(default_factory=lambda: _env_bool("CACHE_ENABLED", True))


@dataclass(frozen=True)
class ApiSettings:
    prefix: str = field(default_factory=lambda: _env("API_PREFIX", "/api/v1"))
    cors_origins: list[str] = field(
        default_factory=lambda: _env_list("CORS_ORIGINS", ["http://localhost:5173", "http://localhost:3000"])
    )
    log_level: str = field(default_factory=lambda: _env("LOG_LEVEL", "INFO"))
    login_rate_limit: str = field(default_factory=lambda: _env("LOGIN_RATE_LIMIT", "5/minute"))

    def __post_init__(self):
        if "*" in self.cors_origins:
            raise ValueError("cors_origins='*' is incompatible with allow_credentials=True")


@dataclass(frozen=True)
class Settings:
    jwt: JwtSettings = field(default_factory=JwtSettings)
    mongo: MongoSettings = field(default_factory=MongoSettings)
    cache: CacheSettings = field(default_factory=CacheSettings)
    api: ApiSettings = field(default_factory=ApiSettings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
