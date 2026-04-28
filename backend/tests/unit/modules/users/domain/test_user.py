from uuid import uuid4

import pytest

from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.users.domain.user import User
from tests.unit.modules._fakes import FakePasswordHasher


def _valid_args(**overrides):
    base = dict(
        id=str(uuid4()),
        name="Alice",
        email="alice@example.com",
        password_hash="hashed::whatever",
        role_id=str(uuid4()),
    )
    base.update(overrides)
    return base


def test_create_happy_path():
    user = User.create(**_valid_args())
    assert user.email.value == "alice@example.com"
    assert user.is_active.value is True


def test_create_aggregates_all_invariant_errors():
    with pytest.raises(DomainValidationError) as exc:
        User.create(**_valid_args(id="not-uuid", email="bad", name=""))

    assert set(exc.value.errors.keys()) == {"id", "email", "name"}


def test_toggle_inverts_active_flag():
    user = User.create(**_valid_args())
    user.toggle()
    assert user.is_active.value is False
    user.toggle()
    assert user.is_active.value is True


def test_change_password_updates_stored_hash():
    hasher = FakePasswordHasher()
    user = User.create(**_valid_args())

    user.change_password("AnotherPass1!", hasher)

    assert user.password.value == "hashed::AnotherPass1!"


def test_change_password_validates_plain_input():
    hasher = FakePasswordHasher()
    user = User.create(**_valid_args())

    with pytest.raises(DomainValidationError) as exc:
        user.change_password("short", hasher)

    assert "password" in exc.value.errors
