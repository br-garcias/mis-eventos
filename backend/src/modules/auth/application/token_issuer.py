from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from modules.shared.domain.security.token_service import TokenClaims, TokenService


@dataclass(frozen=True)
class IssuedAccessToken:
    value: str
    token_id: str
    expires_at: int


class TokenIssuer:
    
    DEFAULT_ACCESS_TOKEN_TTL = timedelta(hours=1)

    def __init__(
        self,
        token_service: TokenService,
        access_ttl: timedelta | None = None,
    ) -> None:
        self._token_service = token_service
        self._access_ttl = access_ttl or self.DEFAULT_ACCESS_TOKEN_TTL

    def issue_access(
        self,
        *,
        session_id: str,
        user_id: str,
        role: str,
        role_id: str,
    ) -> IssuedAccessToken:
        now = int(datetime.now(timezone.utc).timestamp())
        token_id = str(uuid4())
        expires_at = now + int(self._access_ttl.total_seconds())
        claims = TokenClaims(
            session_id=session_id,
            user_id=user_id,
            role=role,
            role_id=role_id,
            token_id=token_id,
            issued_at=now,
            not_before=now,
            expires_at=expires_at,
        )
        return IssuedAccessToken(
            value=self._token_service.generate(claims),
            token_id=token_id,
            expires_at=expires_at,
        )
