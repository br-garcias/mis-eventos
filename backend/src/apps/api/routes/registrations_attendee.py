from __future__ import annotations

import uuid

from fastapi import APIRouter, Request, status

from apps.api.dependencies import get_command_bus, get_query_bus
from modules.registration_views.application.find_by_user.find_registrations_by_user_query import (
    FindRegistrationsByUserQuery,
)
from modules.registration_views.domain.registration_view_dto import MyRegistrationView
from modules.registrations.application.cancel_by_event.cancel_registration_by_event_command import (
    CancelRegistrationByEventCommand,
)
from modules.registrations.application.register.register_to_event_command import (
    RegisterToEventCommand,
)

router = APIRouter(tags=["registrations"])


@router.post("/events/{event_id}/register", status_code=status.HTTP_201_CREATED)
def register_to_event(event_id: str, request: Request):
    auth = request.state.auth
    registration_id = str(uuid.uuid4())
    get_command_bus().dispatch(
        RegisterToEventCommand(
            registration_id=registration_id,
            event_id=event_id,
            user_id=auth.user_id,
        )
    )
    return {"id": registration_id}


@router.delete("/events/{event_id}/register", status_code=status.HTTP_204_NO_CONTENT)
def cancel_registration(event_id: str, request: Request):
    auth = request.state.auth
    get_command_bus().dispatch(
        CancelRegistrationByEventCommand(user_id=auth.user_id, event_id=event_id)
    )
    return None


@router.get("/me/registrations", response_model=dict)
def list_my_registrations(request: Request):
    auth = request.state.auth
    results = get_query_bus().ask(FindRegistrationsByUserQuery(user_id=auth.user_id))
    return {"items": [r.to_primitive() for r in results]}
