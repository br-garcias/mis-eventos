from modules.auth.application.auth_response import AuthResponse
from modules.auth.application.refresh_token_generator import RefreshTokenGenerator
from modules.auth.application.sessions.session_creator import SessionCreator
from modules.auth.application.sessions.session_revoker import SessionRevoker
from modules.auth.application.token_issuer import TokenIssuer
from modules.auth.domain.errors import InvalidRefreshTokenError, SessionExpiredError
from modules.auth.domain.session_repository import SessionRepository


class SessionRenewer:
    def __init__(
        self,
        session_repository: SessionRepository,
        session_revoker: SessionRevoker,
        session_creator: SessionCreator,
        token_issuer: TokenIssuer,
    ) -> None:
        self._session_repository = session_repository
        self._session_revoker = session_revoker
        self._session_creator = session_creator
        self._token_issuer = token_issuer

    def renew(self, refresh_token: str, ip_address: str) -> AuthResponse:
        if not isinstance(refresh_token, str) or not refresh_token:
            raise InvalidRefreshTokenError()

        hashed = RefreshTokenGenerator.hash(refresh_token)
        session = self._session_repository.find_by_refresh_hash(hashed)
        if session is None:
            raise InvalidRefreshTokenError("Session not found")

        self._session_revoker.revoke_by_refresh_hash(hashed)

        if session.is_expired():
            raise SessionExpiredError()

        created = self._session_creator.create(
            user_id=session.user_id.value,
            user_role_id=session.user_role_id.value,
            user_role=session.user_role,
            ip_address=ip_address,
        )

        access = self._token_issuer.issue_access(
            session_id=created.session.id.value,
            user_id=session.user_id.value,
            role=session.user_role,
            role_id=session.user_role_id.value,
        )

        return AuthResponse(
            session_id=created.session.id.value,
            access_token=access.value,
            access_token_expiry=access.expires_at,
            refresh_token=created.refresh_token_plain,
            refresh_token_expiry=int(created.session.expires_at.timestamp()),
        )
