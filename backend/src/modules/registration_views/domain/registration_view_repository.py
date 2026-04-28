from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .registration_view_dto import EventAttendeeView, MyRegistrationView


class RegistrationViewRepository(ABC):
    @abstractmethod
    def find_by_user(self, user_id: str) -> List[MyRegistrationView]: ...

    @abstractmethod
    def find_by_event(self, event_id: str) -> List[EventAttendeeView]: ...

    @abstractmethod
    def invalidate_cache(self) -> None: ...
