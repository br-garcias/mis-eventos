from __future__ import annotations

from modules.event_sessions.domain.errors import (
    SessionOverlapError,
    SessionTimeOutOfBoundsError,
)
from modules.event_sessions.domain.event_session import EventSession
from modules.event_sessions.domain.event_session_repository import EventSessionRepository
from modules.event_views.application.invalidate_cache.invalidate_event_views_cache import (
    InvalidateEventViewsCache,
)
from modules.events.domain.errors import EventNotFoundError
from modules.events.domain.event_repository import EventRepository
from modules.shared.domain.value_object.id_value_object import IdValueObject


class EventSessionCreator:
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
        event_id: str,
        title: str,
        description: str,
        speaker_name: str,
        speaker_bio: str,
        start_at,
        end_at,
    ) -> None:
        event = self._event_repo.find_by_id(IdValueObject(event_id))
        if event is None:
            raise EventNotFoundError(event_id)

        # Validate session dates within event dates
        if start_at < event.dates.start_at or end_at > event.dates.end_at:
            raise SessionTimeOutOfBoundsError(
                f"Session must be between {event.dates.start_at} and {event.dates.end_at}"
            )

        session = EventSession.create(
            id=id,
            event_id=event_id,
            title=title,
            description=description,
            speaker_name=speaker_name,
            speaker_bio=speaker_bio,
            start_at=start_at,
            end_at=end_at,
            event_dates=(event.dates.start_at, event.dates.end_at),
        )

        overlapping = self._session_repo.find_overlapping(
            event_id=IdValueObject(event_id),
            start_at=session.time_range.start_at,
            end_at=session.time_range.end_at,
        )
        if overlapping is not None:
            raise SessionOverlapError(overlapping.id.value)

        self._session_repo.save(session)
        self._cache_invalidator.invalidate_all()
