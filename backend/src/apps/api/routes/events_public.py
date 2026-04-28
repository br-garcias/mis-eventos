from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from apps.api.dependencies import get_query_bus
from modules.event_views.application.find_by_id.find_event_by_id_query import (
    FindEventByIdQuery,
)
from modules.event_views.application.search.search_events_query import SearchEventsQuery
from modules.event_views.domain.event_view_dto import EventDetailView, Page

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=Page)
def list_events(
    q: str | None = None,
    status: str | None = None,
    organizer_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_by: str = "start_at",
    page: int = 1,
    size: int = 20,
    user_id: str | None = None,
):
    return get_query_bus().ask(
        SearchEventsQuery(
            q=q,
            status=status,
            organizer_id=organizer_id,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            page=page,
            size=size,
            user_id=user_id,
        )
    )


@router.get("/{event_id}", response_model=dict)
def get_event(event_id: str, user_id: str | None = None):
    event = get_query_bus().ask(FindEventByIdQuery(id=event_id, user_id=user_id))
    if event is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"code": "EventNotFoundError", "message": f"Event <{event_id}> not found"},
        )
    return event.to_primitive()
