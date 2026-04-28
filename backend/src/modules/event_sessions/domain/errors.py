from __future__ import annotations

from modules.shared.domain.domain_error import ConflictError, NotFoundError, ValidationError


class EventSessionNotFoundError(NotFoundError):
    def __init__(self, session_id: str) -> None:
        super().__init__(f"EventSession <{session_id}> not found")
        self.session_id = session_id


class SessionTimeOutOfBoundsError(ValidationError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Session time is outside event bounds: {reason}")
        self.reason = reason


class SessionOverlapError(ConflictError):
    def __init__(self, session_id: str | None = None) -> None:
        msg = "Session overlaps with another session of the same event"
        if session_id:
            msg += f" <{session_id}>"
        super().__init__(msg)
        self.session_id = session_id
