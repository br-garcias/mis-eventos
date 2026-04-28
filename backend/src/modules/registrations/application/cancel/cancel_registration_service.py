from __future__ import annotations

from modules.events.domain.event_repository import EventRepository
from modules.registration_views.application.invalidate_cache.invalidate_registration_views_cache import (
    InvalidateRegistrationViewsCache,
)
from modules.registrations.domain.errors import RegistrationNotFoundError
from modules.registrations.domain.registration_repository import RegistrationRepository
from modules.shared.domain.value_object.id_value_object import IdValueObject


class CancelRegistrationService:
    def __init__(
        self,
        event_repo: EventRepository,
        registration_repo: RegistrationRepository,
        cache_invalidator: InvalidateRegistrationViewsCache,
    ) -> None:
        self._event_repo = event_repo
        self._registration_repo = registration_repo
        self._cache_invalidator = cache_invalidator

    def run(self, *, registration_id: str, user_id: str) -> None:
        registration = self._registration_repo.find_by_id(IdValueObject(registration_id))
        if registration is None:
            raise RegistrationNotFoundError(registration_id)

        if registration.user_id.value != user_id:
            raise RegistrationNotFoundError(registration_id)

        # Only confirmed registrations can be cancelled
        if registration.status.value != "confirmed":
            return

        registration.cancel()
        self._registration_repo.save(registration)

        self._event_repo.release_spot(registration.event_id)
        self._cache_invalidator.invalidate_all()
