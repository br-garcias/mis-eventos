import pytest

from modules.auth.application.register.attendee_registrar import AttendeeRegistrar
from modules.auth.application.login.user_authenticator import UserAuthenticator
from modules.auth.application.sessions.session_creator import SessionCreator
from modules.auth.application.token_issuer import TokenIssuer
from modules.auth.domain.errors import InvalidCredentialsError
from modules.roles.domain.role_name import RoleName
from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.user_views.application.invalidate_cache.invalidate_user_views_cache import (
    InvalidateUserViewsCache,
)
from modules.user_views.domain.user_view_repository import UserViewRepository
from modules.users.domain.user_already_exists_error import UserAlreadyExistsError
from modules.users.domain.user_repository import UserRepository
from tests.unit.modules._fakes import (
    FakePasswordHasher,
    FakeRoleRepository,
    FakeSessionRepository,
    FakeTokenService,
    FakeUserRepository,
    make_role,
)


class FakeUserViewRepository(UserViewRepository):
    def search(self, *, email=None, role_id=None):
        return []

    def find_by_id(self, id):
        return None

    def invalidate_cache(self) -> None:
        pass


def _build():
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    hasher = FakePasswordHasher()
    token_service = FakeTokenService()
    session_repo = FakeSessionRepository()

    role = make_role(name=RoleName.ATTENDEE.value)
    role_repo.add(role)

    authenticator = UserAuthenticator(
        user_repository=user_repo,
        role_repository=role_repo,
        hasher=hasher,
        token_issuer=TokenIssuer(token_service),
        session_creator=SessionCreator(session_repo),
    )
    cache_invalidator = InvalidateUserViewsCache(FakeUserViewRepository())
    from modules.users.application.create.user_creator import UserCreator
    registrar = AttendeeRegistrar(
        user_creator=UserCreator(user_repo, role_repo, hasher, cache_invalidator),
        user_authenticator=authenticator,
    )
    return registrar, user_repo, hasher, role


def test_register_creates_attendee_and_returns_tokens():
    registrar, user_repo, _, role = _build()

    response = registrar.register(
        name="Alice",
        email="alice@example.com",
        password="Sup3rSecret!",
        ip_address="127.0.0.1",
    )

    assert response.access_token and response.refresh_token
    assert response.session_id
    user = user_repo.find_by_email("alice@example.com")
    assert user is not None
    assert user.role_id.value == role.id.value


def test_register_duplicate_email_raises():
    registrar, _, _, _ = _build()
    registrar.register(name="Alice", email="dup@example.com", password="Sup3rSecret!", ip_address="127.0.0.1")

    with pytest.raises(UserAlreadyExistsError):
        registrar.register(name="Bob", email="dup@example.com", password="Sup3rSecret!", ip_address="127.0.0.1")
