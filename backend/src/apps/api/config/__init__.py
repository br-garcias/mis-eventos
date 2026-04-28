from apps.api.config.settings import get_settings as _get_settings

_cfg = _get_settings()

JWT_SECRET = _cfg.jwt.secret
JWT_ISSUER = _cfg.jwt.issuer
JWT_ACCESS_TTL = _cfg.jwt.access_ttl_seconds
JWT_REFRESH_TTL = _cfg.jwt.refresh_ttl_seconds
VALKEY_URL = _cfg.cache.valkey_url
CACHE_TTL_SECONDS = _cfg.cache.ttl_seconds
CACHE_ENABLED = _cfg.cache.enabled
MONGO_URL = _cfg.mongo.url
LOG_LEVEL = _cfg.api.log_level
LOGIN_RATE_LIMIT = _cfg.api.login_rate_limit
API_PREFIX = _cfg.api.prefix
CORS_ORIGINS = _cfg.api.cors_origins

__all__ = [
    "JWT_SECRET",
    "JWT_ISSUER",
    "JWT_ACCESS_TTL",
    "JWT_REFRESH_TTL",
    "VALKEY_URL",
    "CACHE_TTL_SECONDS",
    "CACHE_ENABLED",
    "MONGO_URL",
    "LOG_LEVEL",
    "LOGIN_RATE_LIMIT",
    "API_PREFIX",
    "CORS_ORIGINS",
]