from __future__ import annotations

from modules.shared.domain.domain_error import ConflictError, NotFoundError


class RegistrationNotFoundError(NotFoundError):
    def __init__(self, registration_id: str) -> None:
        super().__init__(f"Registration <{registration_id}> not found")
        self.registration_id = registration_id


class AlreadyRegisteredError(ConflictError):
    def __init__(self, event_id: str, user_id: str) -> None:
        super().__init__(f"User <{user_id}> is already registered to event <{event_id}>")
        self.event_id = event_id
        self.user_id = user_id


class RegistrationClosedError(ConflictError):
    def __init__(self, event_id: str, reason: str) -> None:
        super().__init__(f"Registration to event <{event_id}> is closed: {reason}")
        self.event_id = event_id
        self.reason = reason


class OrganizerCannotRegisterError(ConflictError):
    def __init__(self, event_id: str, organizer_id: str) -> None:
        super().__init__(f"Organizer <{organizer_id}> cannot register to their own event <{event_id}>")
        self.event_id = event_id
        self.organizer_id = organizer_id
