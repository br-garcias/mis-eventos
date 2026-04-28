from modules.auth.application.auth_data import AuthData
from modules.auth.domain.errors import SessionRevokedError
from modules.auth.domain.session_repository import SessionRepository
from modules.shared.domain.security.token_service import TokenService


class AuthValidator:
    def __init__(
        self,
        token_service: TokenService,
        session_repository: SessionRepository,
    ) -> None:
        self._token_service = token_service
        self._session_repository = session_repository

    def validate(self, token: str) -> AuthData:
        try:
            claims = self._token_service.verify(token)
        except ValueError as e:
            raise PermissionError(f"Unauthorized: {e}") from e

        session = self._session_repository.find_by_id(claims.session_id)
        if session is None:
            raise SessionRevokedError()

        return AuthData.from_claims(claims)
