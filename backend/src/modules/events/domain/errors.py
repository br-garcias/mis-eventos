from __future__ import annotations

from modules.shared.domain.domain_error import ConflictError, NotFoundError


class EventNotFoundError(NotFoundError):
    def __init__(self, event_id: str) -> None:
        super().__init__(f"Event <{event_id}> not found")
        self.event_id = event_id


class InvalidEventStatusTransitionError(ConflictError):
    def __init__(self, current: str, target: str) -> None:
        super().__init__(f"Cannot transition event from <{current}> to <{target}>")
        self.current = current
        self.target = target


class EventNotPublishableError(ConflictError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Event is not publishable: {reason}")
        self.reason = reason


class EventNotEditableError(ConflictError):
    def __init__(self, status: str) -> None:
        super().__init__(f"Event in status <{status}> cannot be edited")
        self.status = status


class EventNotDeletableError(ConflictError):
    def __init__(self, status: str) -> None:
        super().__init__(f"Event in status <{status}> cannot be deleted")
        self.status = status


class EventCapacityBelowConfirmedError(ConflictError):
    def __init__(self, requested: int, confirmed: int) -> None:
        super().__init__(
            f"Cannot set capacity to {requested}: {confirmed} attendees already confirmed"
        )
        self.requested = requested
        self.confirmed = confirmed


class EventFullError(ConflictError):
    def __init__(self, event_id: str) -> None:
        super().__init__(f"Event <{event_id}> is at full capacity")
        self.event_id = event_id


class EventNotPublishedError(ConflictError):
    def __init__(self, event_id: str, status: str) -> None:
        super().__init__(f"Event <{event_id}> is not open for registration (status={status})")
        self.event_id = event_id
        self.status = status
