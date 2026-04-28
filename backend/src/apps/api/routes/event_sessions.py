from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from apps.api.dependencies import get_command_bus
from modules.event_sessions.application.create.create_event_session_command import (
    CreateEventSessionCommand,
)
from modules.event_sessions.application.delete.delete_event_session_command import (
    DeleteEventSessionCommand,
)
from modules.event_sessions.application.update.update_event_session_command import (
    UpdateEventSessionCommand,
)

router = APIRouter(
    prefix="/events/{event_id}/sessions",
    tags=["event-sessions"],
)


# ── Request models ────────────────────────────────────────────────────────────
class CreateSessionRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(default="", max_length=5000)
    speaker_name: str = Field(default="", max_length=200)
    speaker_bio: str = Field(default="", max_length=2000)
    start_at: datetime
    end_at: datetime
    capacity: int | None = Field(default=None, gt=0, le=1_000_000)


class UpdateSessionRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    speaker_name: str | None = Field(default=None, max_length=200)
    speaker_bio: str | None = Field(default=None, max_length=2000)
    start_at: datetime | None = None
    end_at: datetime | None = None
    capacity: int | None = Field(default=None, gt=0, le=1_000_000)


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("", status_code=status.HTTP_201_CREATED)
def create_session(
    event_id: str,
    body: CreateSessionRequest,
):
    session_id = str(uuid.uuid4())
    get_command_bus().dispatch(
        CreateEventSessionCommand(
            id=session_id,
            event_id=event_id,
            title=body.title,
            description=body.description,
            speaker_name=body.speaker_name,
            speaker_bio=body.speaker_bio,
            start_at=body.start_at,
            end_at=body.end_at,
        )
    )
    return {"id": session_id}


@router.patch("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_session(
    event_id: str,
    session_id: str,
    body: UpdateSessionRequest,
):
    get_command_bus().dispatch(
        UpdateEventSessionCommand(
            id=session_id,
            title=body.title,
            description=body.description,
            speaker_name=body.speaker_name,
            speaker_bio=body.speaker_bio,
            start_at=body.start_at,
            end_at=body.end_at,
        )
    )
    return None


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    event_id: str,
    session_id: str,
):
    get_command_bus().dispatch(DeleteEventSessionCommand(id=session_id))
    return None
