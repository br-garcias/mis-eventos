from modules.auth.application.auth_response import AuthResponse
from modules.auth.application.sessions.session_creator import SessionCreator
from modules.auth.application.token_issuer import TokenIssuer
from modules.auth.domain.errors import AccountDisabledError, InvalidCredentialsError
from modules.roles.domain.role_repository import RoleRepository
from modules.shared.domain.security.password_hasher import PasswordHasher
from modules.users.domain.user_repository import UserRepository


class UserAuthenticator:
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        hasher: PasswordHasher,
        token_issuer: TokenIssuer,
        session_creator: SessionCreator,
    ) -> None:
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._hasher = hasher
        self._token_issuer = token_issuer
        self._session_creator = session_creator

    def authenticate(self, email: str, password: str, ip_address: str) -> AuthResponse:
        user = self._user_repository.find_by_email(email)
        if user is None:
            raise InvalidCredentialsError()

        if not user.is_active.value:
            raise AccountDisabledError()

        if not user.password.matches(password, self._hasher):
            raise InvalidCredentialsError()

        role = self._role_repository.find_by_id(user.role_id.value)
        if role is None:
            raise InvalidCredentialsError()

        created = self._session_creator.create(
            user_id=user.id.value,
            user_role_id=role.id.value,
            user_role=role.name.value,
            ip_address=ip_address,
        )

        access = self._token_issuer.issue_access(
            session_id=created.session.id.value,
            user_id=user.id.value,
            role=role.name.value,
            role_id=role.id.value,
        )

        return AuthResponse(
            session_id=created.session.id.value,
            access_token=access.value,
            access_token_expiry=access.expires_at,
            refresh_token=created.refresh_token_plain,
            refresh_token_expiry=int(created.session.expires_at.timestamp()),
        )
