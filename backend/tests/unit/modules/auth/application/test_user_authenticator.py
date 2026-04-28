import pytest

from modules.auth.domain.errors import AccountDisabledError, InvalidCredentialsError

from modules.auth.application.login.user_authenticator import UserAuthenticator
from modules.auth.application.sessions.session_creator import SessionCreator
from modules.auth.application.token_issuer import TokenIssuer
from tests.unit.modules._fakes import (
    FakePasswordHasher,
    FakeRoleRepository,
    FakeSessionRepository,
    FakeTokenService,
    FakeUserRepository,
    make_role,
    make_user,
)


def _build():
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


def test_authenticate_happy_path_creates_session_and_returns_tokens():
    auth, user, password, session_repo = _build()

    response = auth.authenticate(user.email.value, password, "127.0.0.1")

    assert response.access_token and response.refresh_token
    assert response.session_id in session_repo._by_id
    assert response.refresh_token_expiry > response.access_token_expiry > 0
    assert len(session_repo._by_id) == 1


def test_authenticate_unknown_email_raises():
    auth, _, _, _ = _build()
    with pytest.raises(InvalidCredentialsError):
        auth.authenticate("ghost@example.com", "whatever", "127.0.0.1")


def test_authenticate_wrong_password_raises():
    auth, user, _, _ = _build()
    with pytest.raises(InvalidCredentialsError):
        auth.authenticate(user.email.value, "wrong-password", "127.0.0.1")


def test_authenticate_disabled_user_raises_permission():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    session_repo = FakeSessionRepository()
    token_service = FakeTokenService()

    role = make_role("admin")
    role_repo.add(role)
    user, password = make_user(hasher=hasher, role_id=role.id.value, is_active=False)
    user_repo.save(user)

    auth = UserAuthenticator(
        user_repository=user_repo,
        role_repository=role_repo,
        hasher=hasher,
        token_issuer=TokenIssuer(token_service),
        session_creator=SessionCreator(session_repo),
    )

    with pytest.raises(AccountDisabledError):
        auth.authenticate(user.email.value, password, "127.0.0.1")
