"""Unit tests for Auth command and query handlers."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

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
from modules.auth.application.register.register_command_handler import RegisterCommandHandler
from modules.auth.application.sessions.session_creator import SessionCreator
from modules.auth.application.sessions.session_revoker import SessionRevoker
from modules.auth.application.token_issuer import TokenIssuer
from modules.auth.application.validate.auth_validator import AuthValidator
from modules.auth.application.validate.validate_token_query import ValidateTokenQuery
from modules.auth.application.validate.validate_token_query_handler import ValidateTokenQueryHandler
from modules.auth.domain.errors import InvalidCredentialsError
from modules.auth.domain.session import Session
from modules.roles.domain.role_name import RoleName
from modules.users.application.create.user_creator import UserCreator
from tests.unit.modules._fakes import (
    FakeInvalidateCache,
    FakePasswordHasher,
    FakeRoleRepository,
    FakeSessionRepository,
    FakeTokenService,
    FakeUserRepository,
    make_role,
    make_user,
)


def _build_auth():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    session_repo = FakeSessionRepository()
    token_service = FakeTokenService()

    role = make_role("admin")
    role_repo.add(role)
    user, password = make_user(hasher=hasher, role_id=role.id.value)
    user_repo.save(user)

    auth = UserAuthenticator(
        user_repository=user_repo,
        role_repository=role_repo,
        hasher=hasher,
        token_issuer=TokenIssuer(token_service),
        session_creator=SessionCreator(session_repo),
    )
    return auth, user, password, session_repo


def test_login_command_handler():
    auth, user, password, session_repo = _build_auth()
    handler = LoginCommandHandler(auth)
    cmd = LoginCommand(email=user.email.value, password=password, ip_address="127.0.0.1")
    response = handler.handle(cmd)
    assert response.access_token
    assert len(session_repo._by_id) == 1
    assert handler.subscribed_to() == LoginCommand


def test_logout_command_handler():
    session_repo = FakeSessionRepository()
    handler = LogoutCommandHandler(UserLogout(SessionRevoker(session_repo)))
    cmd = LogoutCommand(session_id="some-id")
    handler.handle(cmd)
    assert handler.subscribed_to() == LogoutCommand


def test_refresh_token_command_handler():
    from modules.auth.application.refresh_token_generator import RefreshTokenGenerator
    session_repo = FakeSessionRepository()
    token_service = FakeTokenService()
    issuer = TokenIssuer(token_service)
    session_creator = SessionCreator(session_repo)
    session_revoker = SessionRevoker(session_repo)

    refresh = RefreshTokenGenerator.generate()
    sid = str(uuid4())
    session = Session.create(
        id=sid,
        user_id=str(uuid4()),
        user_role_id=str(uuid4()),
        user_role="admin",
        refresh_token_hash=refresh.hashed,
        ip_address="127.0.0.1",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    session_repo.save(session)

    renewer = SessionRenewer(
        session_repository=session_repo,
        session_revoker=session_revoker,
        session_creator=session_creator,
        token_issuer=issuer,
    )
    handler = RefreshTokenCommandHandler(renewer)
    cmd = RefreshTokenCommand(refresh_token=refresh.plain, ip_address="10.0.0.1")
    response = handler.handle(cmd)
    assert response.access_token
    assert handler.subscribed_to() == RefreshTokenCommand


def test_register_command_handler():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    session_repo = FakeSessionRepository()
    token_service = FakeTokenService()

    role = make_role("attendee")
    role_repo.add(role)

    user_creator = UserCreator(user_repo, role_repo, hasher, FakeInvalidateCache())
    auth = UserAuthenticator(
        user_repository=user_repo,
        role_repository=role_repo,
        hasher=hasher,
        token_issuer=TokenIssuer(token_service),
        session_creator=SessionCreator(session_repo),
    )
    registrar = AttendeeRegistrar(user_creator, auth)
    handler = RegisterCommandHandler(registrar)

    cmd = RegisterCommand(name="Alice", email="alice@example.com", password="Secret123!", ip_address="127.0.0.1")
    response = handler.handle(cmd)
    assert response.access_token
    assert handler.subscribed_to() == RegisterCommand


def test_validate_token_query_handler():
    from modules.shared.domain.security.token_service import TokenClaims
    token_service = FakeTokenService()
    session_repo = FakeSessionRepository()
    sid = str(uuid4())
    uid = str(uuid4())
    rid = str(uuid4())
    claims = TokenClaims(
        session_id=sid,
        user_id=uid,
        role="admin",
        role_id=rid,
        token_id=str(uuid4()),
        issued_at=0,
        not_before=0,
        expires_at=9999999999,
    )
    session = Session.create(
        id=sid,
        user_id=uid,
        user_role_id=rid,
        user_role="admin",
        refresh_token_hash="hash",
        ip_address="127.0.0.1",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    session_repo.save(session)
    token = token_service.generate(claims)
    validator = AuthValidator(token_service, session_repo)
    handler = ValidateTokenQueryHandler(validator)
    cmd = ValidateTokenQuery(token=token)
    result = handler.handle(cmd)
    assert result.user_id is not None
    assert handler.subscribed_to() == ValidateTokenQuery


def test_validate_token_query_handler_invalid():
    from modules.shared.domain.security.token_service import TokenClaims
    token_service = FakeTokenService()
    session_repo = FakeSessionRepository()
    validator = AuthValidator(token_service, session_repo)
    handler = ValidateTokenQueryHandler(validator)
    cmd = ValidateTokenQuery(token="invalid-token")
    with pytest.raises(PermissionError):
        handler.handle(cmd)
