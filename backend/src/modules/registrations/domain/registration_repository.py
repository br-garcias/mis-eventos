from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.domain.value_object.id_value_object import IdValueObject

from .registration import Registration
from .registration_status import RegistrationStatus


class RegistrationRepository(ABC):
    @abstractmethod
    def save(self, registration: Registration) -> None: ...

    @abstractmethod
    def find_by_id(self, id: IdValueObject) -> Registration | None: ...

    @abstractmethod
    def find_by_event_and_user(
        self, event_id: IdValueObject, user_id: IdValueObject
    ) -> Registration | None: ...

    @abstractmethod
    def find_by_user(
        self, user_id: IdValueObject, *, status: RegistrationStatus | None = None
    ) -> list[Registration]: ...

    @abstractmethod
    def find_by_event(
        self, event_id: IdValueObject, *, status: RegistrationStatus | None = None
    ) -> list[Registration]: ...
