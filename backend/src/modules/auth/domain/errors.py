"""Auth bounded-context domain errors.

Replace ad-hoc ``ValueError`` / ``PermissionError`` with explicit, mappable
exceptions so the HTTP layer does not need to catch them.
"""
from __future__ import annotations

from modules.shared.domain.domain_error import AuthenticationError


class AuthError(AuthenticationError):
    """Base class for auth-domain errors."""


class InvalidCredentialsError(AuthError):
    def __init__(self) -> None:
        super().__init__("Invalid credentials")


class AccountDisabledError(AuthError):
    def __init__(self) -> None:
        super().__init__("Account is disabled")


class InvalidRefreshTokenError(AuthError):
    def __init__(self, message: str = "Invalid refresh token") -> None:
        super().__init__(message)


class SessionExpiredError(AuthError):
    def __init__(self) -> None:
        super().__init__("Session expired")


class SessionRevokedError(AuthError):
    def __init__(self) -> None:
        super().__init__("Session revoked")
