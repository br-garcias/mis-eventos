from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from modules.shared.domain.aggregate_root import AggregateRoot
from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError

from .errors import (
    EventCapacityBelowConfirmedError,
    EventFullError,
    EventNotDeletableError,
    EventNotEditableError,
    EventNotPublishableError,
    EventNotPublishedError,
    InvalidEventStatusTransitionError,
)
from .event_capacity import EventCapacity
from .event_date_range import EventDateRange
from .event_description import EventDescription
from .event_name import EventName
from .event_status import EventStatus


@dataclass
class Event(AggregateRoot):
    id: IdValueObject
    name: EventName
    description: EventDescription
    organizer_id: IdValueObject
    capacity: EventCapacity
    confirmed_attendees: int
    dates: EventDateRange
    location: str
    status: EventStatus
    created_at: datetime
    updated_at: datetime

    # ── Construction ──────────────────────────────────────────────────────────
    @classmethod
    def create(
        cls,
        *,
        id: str,
        name: str,
        description: str,
        organizer_id: str,
        capacity: int,
        start_at: datetime,
        end_at: datetime,
        location: str = "",
    ) -> "Event":
        errors: dict[str, list[str]] = {}

        try:
            event_id = IdValueObject(id)
        except InvalidArgumentError as e:
            errors["id"] = [str(e)]

        try:
            event_name = EventName(name)
        except InvalidArgumentError as e:
            errors["name"] = [str(e)]

        try:
            event_description = EventDescription(description or "")
        except InvalidArgumentError as e:
            errors["description"] = [str(e)]

        try:
            organizer = IdValueObject(organizer_id)
        except InvalidArgumentError as e:
            errors["organizer_id"] = [str(e)]

        try:
            event_capacity = EventCapacity(capacity)
        except InvalidArgumentError as e:
            errors["capacity"] = [str(e)]

        try:
            dates = EventDateRange(start_at=start_at, end_at=end_at)
        except InvalidArgumentError as e:
            errors["dates"] = [str(e)]

        if errors:
            raise DomainValidationError(errors)

        now = datetime.now(timezone.utc)
        return cls(
            id=event_id,
            name=event_name,
            description=event_description,
            organizer_id=organizer,
            capacity=event_capacity,
            confirmed_attendees=0,
            dates=dates,
            location=location or "",
            status=EventStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def from_persistence(
        cls,
        *,
        id: IdValueObject,
        name: EventName,
        description: EventDescription,
        organizer_id: IdValueObject,
        capacity: EventCapacity,
        confirmed_attendees: int,
        dates: EventDateRange,
        location: str,
        status: EventStatus,
        created_at: datetime,
        updated_at: datetime,
    ) -> "Event":
        """Hydrate an aggregate from DB fields (VOs already validated)."""
        return cls(
            id=id,
            name=name,
            description=description,
            organizer_id=organizer_id,
            capacity=capacity,
            confirmed_attendees=confirmed_attendees,
            dates=dates,
            location=location,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
        )

    # ── Derived ───────────────────────────────────────────────────────────────
    @property
    def available_spots(self) -> int:
        return max(self.capacity.value - self.confirmed_attendees, 0)

    def is_full(self) -> bool:
        return self.confirmed_attendees >= self.capacity.value

    # ── Editing ───────────────────────────────────────────────────────────────
    def update_details(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        location: str | None = None,
    ) -> None:
        self._ensure_editable()
        errors: dict[str, list[str]] = {}
        if name is not None:
            try:
                self.name = EventName(name)
            except InvalidArgumentError as e:
                errors["name"] = [str(e)]
        if description is not None:
            try:
                self.description = EventDescription(description)
            except InvalidArgumentError as e:
                errors["description"] = [str(e)]
        if location is not None:
            self.location = location
        if errors:
            raise DomainValidationError(errors)
        self._touch()

    def reschedule(self, *, start_at: datetime, end_at: datetime) -> None:
        self._ensure_editable()
        try:
            self.dates = EventDateRange(start_at=start_at, end_at=end_at)
        except InvalidArgumentError as e:
            raise DomainValidationError({"dates": [str(e)]})
        self._touch()

    def change_capacity(self, capacity: int) -> None:
        self._ensure_editable()
        try:
            new_capacity = EventCapacity(capacity)
        except InvalidArgumentError as e:
            raise DomainValidationError({"capacity": [str(e)]})
        if new_capacity.value < self.confirmed_attendees:
            raise EventCapacityBelowConfirmedError(new_capacity.value, self.confirmed_attendees)
        self.capacity = new_capacity
        self._touch()

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def publish(self) -> None:
        if self.status != EventStatus.DRAFT:
            raise InvalidEventStatusTransitionError(self.status.value, EventStatus.PUBLISHED.value)
        if self.capacity.value <= 0:
            raise EventNotPublishableError("capacity must be greater than zero")
        self.status = EventStatus.PUBLISHED
        self._touch()

    def mark_ongoing(self) -> None:
        if self.status != EventStatus.PUBLISHED:
            raise InvalidEventStatusTransitionError(self.status.value, EventStatus.ONGOING.value)
        self.status = EventStatus.ONGOING
        self._touch()

    def finish(self) -> None:
        if self.status != EventStatus.ONGOING:
            raise InvalidEventStatusTransitionError(self.status.value, EventStatus.FINISHED.value)
        self.status = EventStatus.FINISHED
        self._touch()

    def cancel(self) -> None:
        if self.status in (EventStatus.FINISHED, EventStatus.CANCELLED):
            raise InvalidEventStatusTransitionError(self.status.value, EventStatus.CANCELLED.value)
        self.status = EventStatus.CANCELLED
        self._touch()

    # ── Deletion guard ────────────────────────────────────────────────────────
    def ensure_deletable(self) -> None:
        if self.status not in (EventStatus.DRAFT, EventStatus.CANCELLED):
            raise EventNotDeletableError(self.status.value)

    # ── Capacity bookkeeping (used by registrations BC) ───────────────────────
    def reserve_spot(self) -> None:
        if self.status != EventStatus.PUBLISHED:
            raise EventNotPublishedError(self.id.value, self.status.value)
        if self.is_full():
            raise EventFullError(self.id.value)
        self.confirmed_attendees += 1
        self._touch()

    def release_spot(self) -> None:
        if self.confirmed_attendees > 0:
            self.confirmed_attendees -= 1
            self._touch()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _ensure_editable(self) -> None:
        if self.status not in (EventStatus.DRAFT, EventStatus.PUBLISHED):
            raise EventNotEditableError(self.status.value)

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
