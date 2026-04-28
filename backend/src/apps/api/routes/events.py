from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field

from apps.api.dependencies import get_command_bus, get_query_bus
from modules.event_views.application.find_by_organizer.find_my_events_query import (
    FindMyEventsQuery,
)
from modules.events.application.cancel.cancel_event_command import CancelEventCommand
from modules.events.application.create.create_event_command import CreateEventCommand
from modules.events.application.delete.delete_event_command import DeleteEventCommand
from modules.events.application.publish.publish_event_command import PublishEventCommand
from modules.events.application.update.update_event_command import UpdateEventCommand

router = APIRouter(prefix="/events", tags=["events"])


# ── Request models ────────────────────────────────────────────────────────────
class CreateEventRequest(BaseModel):
    name: str = Field(min_length=3, max_length=200)
    description: str = Field(default="", max_length=5000)
    capacity: int = Field(gt=0, le=1_000_000)
    start_at: datetime
    end_at: datetime
    location: str = Field(default="", max_length=500)


class UpdateEventRequest(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    capacity: int | None = Field(default=None, gt=0, le=1_000_000)
    start_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = Field(default=None, max_length=500)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _actor_from_auth(auth) -> tuple[str, str]:
    return auth.user_id, auth.role


# ── Writes ────────────────────────────────────────────────────────────────────
@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(body: CreateEventRequest, request: Request):
    auth = request.state.auth
    event_id = str(uuid.uuid4())
    get_command_bus().dispatch(
        CreateEventCommand(
            id=event_id,
            name=body.name,
            description=body.description,
            organizer_id=auth.user_id,
            capacity=body.capacity,
            start_at=body.start_at,
            end_at=body.end_at,
            location=body.location,
        )
    )
    return {"id": event_id}


@router.patch("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_event(event_id: str, body: UpdateEventRequest, request: Request):
    user_id, role = _actor_from_auth(request.state.auth)
    get_command_bus().dispatch(
        UpdateEventCommand(
            id=event_id,
            actor_user_id=user_id,
            actor_role=role,
            name=body.name,
            description=body.description,
            location=body.location,
            start_at=body.start_at,
            end_at=body.end_at,
            capacity=body.capacity,
        )
    )
    return None


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: str, request: Request):
    user_id, role = _actor_from_auth(request.state.auth)
    get_command_bus().dispatch(
        DeleteEventCommand(id=event_id, actor_user_id=user_id, actor_role=role)
    )
    return None


@router.post("/{event_id}/publish", status_code=status.HTTP_204_NO_CONTENT)
def publish_event(event_id: str, request: Request):
    user_id, role = _actor_from_auth(request.state.auth)
    get_command_bus().dispatch(
        PublishEventCommand(id=event_id, actor_user_id=user_id, actor_role=role)
    )
    return None


@router.post("/{event_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
def cancel_event(event_id: str, request: Request):
    user_id, role = _actor_from_auth(request.state.auth)
    get_command_bus().dispatch(
        CancelEventCommand(id=event_id, actor_user_id=user_id, actor_role=role)
    )
    return None


@router.get("/me/list", response_model=dict)
def list_my_events(
    request: Request,
    q: str | None = None,
    status: str | None = None,
    page: int = 1,
    size: int = 20,
):
    auth = request.state.auth
    return get_query_bus().ask(
        FindMyEventsQuery(
            organizer_id=auth.user_id,
            q=q,
            status=status,
            page=page,
            size=size,
        )
    ).to_primitive()


