"""Write-side port for EventSession."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from modules.shared.domain.value_object.id_value_object import IdValueObject

from .event_session import EventSession


class EventSessionRepository(ABC):
    @abstractmethod
    def save(self, session: EventSession) -> None: ...

    @abstractmethod
    def find_by_id(self, id: IdValueObject) -> EventSession | None: ...

    @abstractmethod
    def find_by_event(self, event_id: IdValueObject) -> list[EventSession]: ...

    @abstractmethod
    def find_overlapping(
        self,
        *,
        event_id: IdValueObject,
        start_at: datetime,
        end_at: datetime,
        exclude_id: IdValueObject | None = None,
    ) -> EventSession | None: ...

    @abstractmethod
    def delete(self, id: IdValueObject) -> None: ...
