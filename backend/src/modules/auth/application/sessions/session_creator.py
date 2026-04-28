from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from modules.auth.application.refresh_token_generator import RefreshToken, RefreshTokenGenerator
from modules.auth.domain.session import Session
from modules.auth.domain.session_repository import SessionRepository
from modules.shared.domain.value_object.id_value_object import IdValueObject


@dataclass(frozen=True)
class CreatedSession:
    session: Session
    refresh_token_plain: str


class SessionCreator:
    DEFAULT_REFRESH_TTL = timedelta(days=7)

    def __init__(
        self,
        session_repository: SessionRepository,
        refresh_ttl: timedelta | None = None,
    ) -> None:
        self._session_repository = session_repository
        self._refresh_ttl = refresh_ttl or self.DEFAULT_REFRESH_TTL

    def create(
        self,
        *,
        user_id: str,
        user_role_id: str,
        user_role: str,
        ip_address: str,
    ) -> CreatedSession:
        refresh = RefreshTokenGenerator.generate()
        expires_at = datetime.now(timezone.utc) + self._refresh_ttl
        session = Session.create(
            id=IdValueObject.random().value,
            user_id=user_id,
            user_role_id=user_role_id,
            user_role=user_role,
            refresh_token_hash=refresh.hashed,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        self._session_repository.save(session)
        return CreatedSession(session=session, refresh_token_plain=refresh.plain)
