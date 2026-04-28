from __future__ import annotations

from modules.registrations.domain.errors import RegistrationNotFoundError
from modules.registrations.domain.registration_repository import RegistrationRepository
from modules.shared.domain.value_object.id_value_object import IdValueObject


class CancelRegistrationByEventService:
    def __init__(
        self,
        registration_repo: RegistrationRepository,
        cancel_service,
    ) -> None:
        self._registration_repo = registration_repo
        self._cancel_service = cancel_service

    def run(self, *, event_id: str, user_id: str) -> None:
        registration = self._registration_repo.find_by_event_and_user(
            IdValueObject(event_id),
            IdValueObject(user_id),
        )
        if registration is None:
            raise RegistrationNotFoundError(event_id)

        self._cancel_service.run(
            registration_id=registration.id.value,
            user_id=user_id,
        )
