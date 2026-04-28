from datetime import timedelta
from typing import Any, Callable, Dict, Type

from modules.auth.application.login.login_command import LoginCommand
from modules.auth.application.login.login_command_handler import LoginCommandHandler
from modules.auth.application.login.user_authenticator import UserAuthenticator
from modules.auth.application.logout.logout_command import LogoutCommand
from modules.auth.application.logout.logout_command_handler import LogoutCommandHandler
from modules.auth.application.logout.user_logout import UserLogout
from modules.auth.application.refresh.refresh_token_command import RefreshTokenCommand
from modules.auth.application.refresh.refresh_token_command_handler import RefreshTokenCommandHandler
from modules.auth.application.refresh.session_renewer import SessionRenewer
from modules.auth.application.register.attendee_registrar import AttendeeRegistrar
from modules.auth.application.register.register_command import RegisterCommand
from modules.auth.application.register.register_command_handler import (
    RegisterCommandHandler,
)
from modules.auth.application.sessions.session_creator import SessionCreator
from modules.auth.application.sessions.session_revoker import SessionRevoker
from modules.auth.application.token_issuer import TokenIssuer
from modules.auth.application.validate.auth_validator import AuthValidator
from modules.auth.application.validate.validate_token_query import ValidateTokenQuery
from modules.auth.application.validate.validate_token_query_handler import (
    ValidateTokenQueryHandler,
)
from modules.auth.infrastructure.persistence.valkey_session_repository import (
    ValkeySessionRepository,
)
from modules.shared.domain.command import Command
from modules.shared.domain.query import Query
from modules.users.application.create.user_creator import UserCreator

from apps.api.config import JWT_ACCESS_TTL, JWT_REFRESH_TTL
from .roles_di import role_repository
from .shared_di import password_hasher, token_service, valkey_client
from .user_views_di import user_view_cache_invalidator
from .users_di import user_repository

_session_repository = ValkeySessionRepository(valkey_client)
_session_creator = SessionCreator(
    _session_repository,
    refresh_ttl=timedelta(seconds=JWT_REFRESH_TTL),
)
_session_revoker = SessionRevoker(_session_repository)

token_issuer = TokenIssuer(
    token_service,
    access_ttl=timedelta(seconds=JWT_ACCESS_TTL),
)


def auth_command_handlers() -> Dict[Type[Command], Callable[[Command], Any]]:
    user_authenticator = UserAuthenticator(
        user_repository=user_repository,
        role_repository=role_repository,
        hasher=password_hasher,
        token_issuer=token_issuer,
        session_creator=_session_creator,
    )
    user_logout = UserLogout(_session_revoker)
    session_renewer = SessionRenewer(
        session_repository=_session_repository,
        session_revoker=_session_revoker,
        session_creator=_session_creator,
        token_issuer=token_issuer,
    )
    attendee_registrar = AttendeeRegistrar(
        user_creator=UserCreator(
            user_repository,
            role_repository,
            password_hasher,
            user_view_cache_invalidator,
        ),
        user_authenticator=user_authenticator,
    )

    return {
        LoginCommand: LoginCommandHandler(user_authenticator),
        LogoutCommand: LogoutCommandHandler(user_logout),
        RefreshTokenCommand: RefreshTokenCommandHandler(session_renewer),
        RegisterCommand: RegisterCommandHandler(attendee_registrar),
    }


def auth_query_handlers() -> Dict[Type[Query], Callable[[Query], Any]]:
    auth_validator = AuthValidator(token_service, _session_repository)

    return {
        ValidateTokenQuery: ValidateTokenQueryHandler(auth_validator),
    }
