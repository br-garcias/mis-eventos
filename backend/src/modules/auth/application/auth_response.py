from dataclasses import dataclass

from modules.shared.domain.response import Response


@dataclass(frozen=True)
class AuthResponse(Response):
    session_id: str
    access_token: str
    access_token_expiry: int
    refresh_token: str
    refresh_token_expiry: int
