from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from modules.shared.domain.aggregate_root import AggregateRoot
from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError

from .errors import AlreadyRegisteredError, RegistrationClosedError
from .registration_status import RegistrationStatus


@dataclass
class Registration(AggregateRoot):
    id: IdValueObject
    event_id: IdValueObject
    user_id: IdValueObject
    status: RegistrationStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        id: str,
        event_id: str,
        user_id: str,
    ) -> "Registration":
        errors: dict[str, list[str]] = {}

        try:
            rid = IdValueObject(id)
        except InvalidArgumentError as e:
            errors["id"] = [str(e)]

        try:
            eid = IdValueObject(event_id)
        except InvalidArgumentError as e:
            errors["event_id"] = [str(e)]

        try:
            uid = IdValueObject(user_id)
        except InvalidArgumentError as e:
            errors["user_id"] = [str(e)]

        if errors:
            raise DomainValidationError(errors)

        now = datetime.now(timezone.utc)
        return cls(
            id=rid,
            event_id=eid,
            user_id=uid,
            status=RegistrationStatus.CONFIRMED,
            created_at=now,
            updated_at=now,
        )

    def cancel(self) -> None:
        if self.status == RegistrationStatus.CANCELLED:
            raise RegistrationClosedError(
                self.event_id.value, "registration is already cancelled"
            )
        self.status = RegistrationStatus.CANCELLED
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
