from uuid import uuid4

import pytest

from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.user_views.application.invalidate_cache.invalidate_user_views_cache import (
    InvalidateUserViewsCache,
)
from modules.user_views.domain.user_view_repository import UserViewRepository
from modules.users.application.create.user_creator import UserCreator
from modules.users.domain.user_already_exists_error import UserAlreadyExistsError
from tests.unit.modules._fakes import (
    FakePasswordHasher,
    FakeRoleRepository,
    FakeUserRepository,
    make_role,
    make_user,
)


class FakeUserViewRepository(UserViewRepository):
    def search(self, *, email=None, role_id=None):
        return []

    def find_by_id(self, id):
        return None

    def invalidate_cache(self) -> None:
        pass


def _build():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    role_repo.add(make_role("admin"))
    cache_invalidator = InvalidateUserViewsCache(FakeUserViewRepository())
    return UserCreator(user_repo, role_repo, hasher, cache_invalidator), user_repo, hasher


def test_creates_user_with_hashed_password():
    creator, user_repo, hasher = _build()

    creator.run(
        id=str(uuid4()),
        name="Alice",
        email="alice@example.com",
        password="Sup3rSecret!",
        role_name="admin",
    )

    saved = user_repo.find_by_email("alice@example.com")
    assert saved is not None
    assert saved.password.value == hasher.hash("Sup3rSecret!")


def test_rejects_duplicate_email():
    creator, user_repo, hasher = _build()
    existing, _ = make_user(hasher=hasher, email="dup@example.com")
    user_repo.save(existing)

    with pytest.raises(UserAlreadyExistsError):
        creator.run(
            id=str(uuid4()),
            name="Bob",
            email="dup@example.com",
            password="Sup3rSecret!",
            role_name="admin",
        )


def test_rejects_unknown_role():
    creator, _, _ = _build()
    with pytest.raises(DomainValidationError) as exc:
        creator.run(
            id=str(uuid4()),
            name="Bob",
            email="bob@example.com",
            password="Sup3rSecret!",
            role_name="nonexistent",
        )
    assert "role_name" in exc.value.errors
