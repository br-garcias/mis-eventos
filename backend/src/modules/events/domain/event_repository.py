from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.domain.value_object.id_value_object import IdValueObject

from .event import Event


class EventRepository(ABC):
    """Write-side port for `Event`. Read concerns live in `event_views`."""

    @abstractmethod
    def save(self, event: Event) -> None: ...

    @abstractmethod
    def find_by_id(self, id: IdValueObject) -> Event | None: ...

    @abstractmethod
    def delete(self, id: IdValueObject) -> None: ...

    @abstractmethod
    def reserve_spot(self, id: IdValueObject) -> bool: ...

    @abstractmethod
    def release_spot(self, id: IdValueObject) -> bool: ...
