from __future__ import annotations

from fastapi import APIRouter, Request

from apps.api.dependencies import get_query_bus
from modules.registration_views.application.find_by_event.find_attendees_by_event_query import (
    FindAttendeesByEventQuery,
)
from modules.registration_views.domain.registration_view_dto import EventAttendeeView

router = APIRouter(tags=["registrations"])


@router.get("/events/{event_id}/attendees", response_model=dict)
def list_event_attendees(event_id: str, request: Request):
    auth = request.state.auth
    results = get_query_bus().ask(
        FindAttendeesByEventQuery(
            event_id=event_id,
            actor_user_id=auth.user_id,
            actor_role=auth.role,
        )
    )
    return {"items": [r.to_primitive() for r in results]}
