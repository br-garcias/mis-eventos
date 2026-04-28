import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from apps.api.exception_handlers import register_exception_handlers
from apps.api.middleware.access_log import AccessLogMiddleware
from apps.api.middleware.request_context import RequestContextMiddleware
from apps.api.rate_limit import limiter
from apps.api.routes import register_routes
from apps.api.config import CORS_ORIGINS, LOG_LEVEL

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from modules.shared.infrastructure.persistence.mongo.mongo_indexes import apply_indexes
    from apps.api.di.shared_di import mongo_client
    apply_indexes(mongo_client.get_database())
    yield


app = FastAPI(
    title="Mis Eventos API",
    version="0.1.0",
    description="Backend API for Mis Eventos platform",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "auth",    "description": "Authentication: login, refresh, logout, me."},
        {"name": "users",   "description": "User management (admin only)."},
        {"name": "events",  "description": "Event CRUD, lifecycle, search, and registration."},
    ],
    swagger_ui_parameters={"persistAuthorization": True},
)

register_exception_handlers(app)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def _handle_rate_limit_exceeded(request, exc: RateLimitExceeded):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=429,
        content={"code": "RateLimitExceeded", "message": str(exc)},
    )


# ── Middleware ─────────────────────────────────────────────────────────────────
# Order matters: outermost is added LAST. RequestContext is the outermost layer.
# Auth + role guards live as router-level dependencies in ``apps.api.routes``
# (see ``register_routes``), mirroring the Go reference project.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-request-id"],
)

app.add_middleware(AccessLogMiddleware)

app.add_middleware(SlowAPIMiddleware)

# Outermost layer — runs first on the way in and last on the way out.
app.add_middleware(RequestContextMiddleware)

# ── Routes ────────────────────────────────────────────────────────────────────
register_routes(app)
