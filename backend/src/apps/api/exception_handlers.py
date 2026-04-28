from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from modules.auth.domain.errors import (
    AccountDisabledError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    SessionExpiredError,
    SessionRevokedError,
)
from modules.auth.domain.session_not_found_error import SessionNotFoundError
from modules.event_sessions.domain.errors import (
    EventSessionNotFoundError,
    SessionOverlapError,
    SessionTimeOutOfBoundsError,
)
from modules.events.application.authorization import EventForbiddenError
from modules.events.domain.errors import (
    EventCapacityBelowConfirmedError,
    EventFullError,
    EventNotDeletableError,
    EventNotEditableError,
    EventNotFoundError,
    EventNotPublishableError,
    EventNotPublishedError,
    InvalidEventStatusTransitionError,
)
from modules.registrations.domain.errors import (
    AlreadyRegisteredError,
    OrganizerCannotRegisterError,
    RegistrationClosedError,
    RegistrationNotFoundError,
)
from modules.shared.domain.domain_error import DomainError
from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.users.domain.user_already_exists_error import UserAlreadyExistsError
from modules.users.domain.user_not_found_error import UserNotFoundError


# ── Error → status mapping (single source of truth) ──────────────────────────
_STATUS = {
    # 401
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    AccountDisabledError: status.HTTP_401_UNAUTHORIZED,
    InvalidRefreshTokenError: status.HTTP_401_UNAUTHORIZED,
    SessionExpiredError: status.HTTP_401_UNAUTHORIZED,
    SessionRevokedError: status.HTTP_401_UNAUTHORIZED,
    # 404
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    SessionNotFoundError: status.HTTP_404_NOT_FOUND,
    EventNotFoundError: status.HTTP_404_NOT_FOUND,
    EventSessionNotFoundError: status.HTTP_404_NOT_FOUND,
    RegistrationNotFoundError: status.HTTP_404_NOT_FOUND,
    # 403
    EventForbiddenError: status.HTTP_403_FORBIDDEN,
    # 409
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    InvalidEventStatusTransitionError: status.HTTP_409_CONFLICT,
    EventNotPublishableError: status.HTTP_409_CONFLICT,
    EventNotEditableError: status.HTTP_409_CONFLICT,
    EventNotDeletableError: status.HTTP_409_CONFLICT,
    EventCapacityBelowConfirmedError: status.HTTP_409_CONFLICT,
    EventFullError: status.HTTP_409_CONFLICT,
    EventNotPublishedError: status.HTTP_409_CONFLICT,
    SessionOverlapError: status.HTTP_409_CONFLICT,
    AlreadyRegisteredError: status.HTTP_409_CONFLICT,
    OrganizerCannotRegisterError: status.HTTP_409_CONFLICT,
    RegistrationClosedError: status.HTTP_409_CONFLICT,
    # 422
    SessionTimeOutOfBoundsError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    DomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def _error_payload(exc: Exception, *, details: dict | list | None = None) -> dict:
    payload: dict = {
        "code": exc.__class__.__name__,
        "message": str(exc),
    }
    if details is not None:
        payload["details"] = details
    return payload


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        code = _STATUS.get(type(exc), 500)
        for cls, status_code in _STATUS.items():
            if isinstance(exc, cls):
                code = status_code
                break

        details = None
        if isinstance(exc, DomainValidationError):
            details = exc.errors

        return JSONResponse(
            status_code=code,
            content=_error_payload(exc, details=details),
        )

    @app.exception_handler(HTTPException)
    async def _handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        content: dict = {"code": exc.__class__.__name__, "message": str(exc.detail)}
        if isinstance(exc.detail, dict):
            content = exc.detail
        return JSONResponse(status_code=exc.status_code, content=content)
