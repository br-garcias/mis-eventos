from __future__ import annotations

from modules.events.domain.errors import EventNotFoundError
from modules.events.domain.event_repository import EventRepository
from modules.registration_views.application.invalidate_cache.invalidate_registration_views_cache import (
    InvalidateRegistrationViewsCache,
)
from modules.registrations.domain.errors import (
    AlreadyRegisteredError,
    OrganizerCannotRegisterError,
    RegistrationClosedError,
)
from modules.registrations.domain.registration import Registration
from modules.registrations.domain.registration_repository import RegistrationRepository
from modules.shared.domain.value_object.id_value_object import IdValueObject


def _closed_reason(event) -> str:
    if event.status.value != "published":
        return f"event is {event.status.value}, must be published"
    return "event is full"


class RegisterToEventService:
    def __init__(
        self,
        event_repo: EventRepository,
        registration_repo: RegistrationRepository,
        cache_invalidator: InvalidateRegistrationViewsCache,
    ) -> None:
        self._event_repo = event_repo
        self._registration_repo = registration_repo
        self._cache_invalidator = cache_invalidator

    def run(self, *, registration_id: str, event_id: str, user_id: str) -> None:
        event = self._event_repo.find_by_id(IdValueObject(event_id))
        if event is None:
            raise EventNotFoundError(event_id)

        # Organizer cannot register to their own event
        if event.organizer_id.value == user_id:
            raise OrganizerCannotRegisterError(event_id, user_id)

        # Unique active registration per user-event
        existing = self._registration_repo.find_by_event_and_user(
            IdValueObject(event_id), IdValueObject(user_id)
        )
        if existing is not None and existing.status.value == "confirmed":
            raise AlreadyRegisteredError(event_id, user_id)

        # Atomic spot reservation on the event
        reserved = self._event_repo.reserve_spot(IdValueObject(event_id))
        if not reserved:
            raise RegistrationClosedError(
                event_id,
                _closed_reason(event),
            )

        # Create and save registration — compensate if persistence fails
        try:
            registration = Registration.create(
                id=registration_id,
                event_id=event_id,
                user_id=user_id,
            )
            self._registration_repo.save(registration)
        except Exception:
            self._event_repo.release_spot(IdValueObject(event_id))
            raise

        self._cache_invalidator.invalidate_all()
