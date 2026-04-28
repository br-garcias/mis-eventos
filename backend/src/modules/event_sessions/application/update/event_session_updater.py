from __future__ import annotations

from modules.event_sessions.domain.errors import (
    EventSessionNotFoundError,
    SessionOverlapError,
)
from modules.event_sessions.domain.event_session_repository import EventSessionRepository
from modules.event_views.application.invalidate_cache.invalidate_event_views_cache import (
    InvalidateEventViewsCache,
)
from modules.events.domain.errors import EventNotFoundError
from modules.events.domain.event_repository import EventRepository
from modules.shared.domain.value_object.id_value_object import IdValueObject


class EventSessionUpdater:
    def __init__(
        self,
        event_repo: EventRepository,
        session_repo: EventSessionRepository,
        cache_invalidator: InvalidateEventViewsCache,
    ) -> None:
        self._event_repo = event_repo
        self._session_repo = session_repo
        self._cache_invalidator = cache_invalidator

    def run(
        self,
        *,
        id: str,
        title: str | None = None,
        description: str | None = None,
        speaker_name: str | None = None,
        speaker_bio: str | None = None,
        start_at=None,
        end_at=None,
    ) -> None:
        session = self._session_repo.find_by_id(IdValueObject(id))
        if session is None:
            raise EventSessionNotFoundError(id)

        event = self._event_repo.find_by_id(session.event_id)
        if event is None:
            raise EventNotFoundError(session.event_id.value)

        # Update details
        session.update_details(
            title=title,
            description=description,
            speaker_name=speaker_name,
            speaker_bio=speaker_bio,
        )

        # Reschedule
        if start_at is not None or end_at is not None:
            new_start = start_at if start_at is not None else session.time_range.start_at
            new_end = end_at if end_at is not None else session.time_range.end_at
            session.reschedule(
                start_at=new_start,
                end_at=new_end,
                event_dates=(event.dates.start_at, event.dates.end_at),
            )

        # Check overlap after potential reschedule
        overlapping = self._session_repo.find_overlapping(
            event_id=session.event_id,
            start_at=session.time_range.start_at,
            end_at=session.time_range.end_at,
            exclude_id=session.id,
        )
        if overlapping is not None:
            raise SessionOverlapError(overlapping.id.value)

        self._session_repo.save(session)
        self._cache_invalidator.invalidate_all()
