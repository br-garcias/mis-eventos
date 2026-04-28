"""Centralised route registration.

Mirrors the pattern of ``internal/_platform/server/routes.go`` in the Go
reference project: a single function declares the public/private groups
and applies the auth + role guards in one auditable place.
"""
from fastapi import APIRouter, Depends, FastAPI

from apps.api.middleware.auth_middleware import authenticate
from apps.api.middleware.require_roles import require_roles

from .auth import router as auth_public_router
from .event_sessions import router as event_sessions_router
from .events import router as events_router
from .events_public import router as events_public_router
from .health import router as health_router
from .me import router as me_router
from .registrations_attendee import router as registrations_attendee_router
from .registrations_organizer import router as registrations_organizer_router
from .roles import router as roles_router
from .users import router as users_router


def register_routes(app: FastAPI) -> None:
    # ── Top-level (no prefix) ─────────────────────────────────────────────
    app.include_router(health_router)

    v1 = APIRouter(prefix="/api/v1")

    # ── Public ────────────────────────────────────────────────────────────
    v1.include_router(auth_public_router)        # /auth/login, /auth/register, /auth/refresh
    v1.include_router(events_public_router)      # GET /events, GET /events/{id}

    # ── Private (authenticated) ───────────────────────────────────────────
    private = APIRouter(dependencies=[Depends(authenticate)])

    private.include_router(me_router)            # /auth/logout, /auth/me

    private.include_router(
        users_router,
        dependencies=[Depends(require_roles("admin"))],
    )
    private.include_router(
        roles_router,
        dependencies=[Depends(require_roles("admin"))],
    )
    private.include_router(
        events_router,
        dependencies=[Depends(require_roles("admin", "organizer"))],
    )
    private.include_router(
        event_sessions_router,
        dependencies=[Depends(require_roles("admin", "organizer"))],
    )
    private.include_router(
        registrations_attendee_router,
        dependencies=[Depends(require_roles("admin", "organizer", "attendee"))],
    )
    private.include_router(
        registrations_organizer_router,
        dependencies=[Depends(require_roles("admin", "organizer"))],
    )

    v1.include_router(private)
    app.include_router(v1)


__all__ = ["register_routes"]
