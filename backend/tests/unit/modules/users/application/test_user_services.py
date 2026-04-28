"""Unit tests for User application services and handlers."""
from uuid import uuid4

import pytest

from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.users.application.change_password.change_password_command import ChangePasswordCommand
from modules.users.application.change_password.change_password_command_handler import ChangePasswordCommandHandler
from modules.users.application.change_password.password_changer import InvalidCurrentPasswordError, PasswordChanger
from modules.users.application.create.create_user_command import CreateUserCommand
from modules.users.application.create.create_user_command_handler import CreateUserCommandHandler
from modules.users.application.create.user_creator import UserCreator
from modules.users.application.toggle.toggle_user_command import ToggleUserCommand
from modules.users.application.toggle.toggle_user_command_handler import ToggleUserCommandHandler
from modules.users.application.toggle.user_toggler import UserToggler
from modules.users.application.update.update_user_command import UpdateUserCommand
from modules.users.application.update.update_user_command_handler import UpdateUserCommandHandler
from modules.users.application.update.user_updater import UserUpdater
from modules.users.domain.user_not_found_error import UserNotFoundError
from tests.unit.modules._fakes import (
    FakeInvalidateCache,
    FakePasswordHasher,
    FakeRoleRepository,
    FakeTokenService,
    FakeUserRepository,
    make_role,
    make_user,
)


def test_user_creator_success():
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    hasher = FakePasswordHasher()
    cache = FakeInvalidateCache()
    role = make_role("admin")
    role_repo.add(role)
    creator = UserCreator(user_repo, role_repo, hasher, cache)
    uid = str(uuid4())
    creator.run(id=uid, name="Alice", email="alice@example.com", password="Secret123!", role_name="admin")
    assert user_repo.find_by_id(IdValueObject(uid)) is not None
    assert cache.calls == 1


def test_password_changer_success():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    cache = FakeInvalidateCache()
    user, password = make_user(hasher=hasher)
    user_repo.save(user)

    changer = PasswordChanger(user_repo, hasher, cache)
    changer.run(user.id.value, password, "NewSecret123!")

    updated = user_repo.find_by_id(user.id)
    assert updated.password.value == "hashed::NewSecret123!"
    assert cache.calls == 1


def test_password_changer_user_not_found():
    hasher = FakePasswordHasher()
    changer = PasswordChanger(FakeUserRepository(), hasher, FakeInvalidateCache())
    with pytest.raises(UserNotFoundError):
        changer.run(str(uuid4()), "old", "new")


def test_password_changer_wrong_password():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    user, password = make_user(hasher=hasher)
    user_repo.save(user)

    changer = PasswordChanger(user_repo, hasher, FakeInvalidateCache())
    with pytest.raises(InvalidCurrentPasswordError):
        changer.run(user.id.value, "wrong", "NewSecret123!")


def test_password_changer_same_password():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    user, password = make_user(hasher=hasher)
    user_repo.save(user)

    changer = PasswordChanger(user_repo, hasher, FakeInvalidateCache())
    with pytest.raises(ValueError):
        changer.run(user.id.value, password, password)


def test_password_changer_disabled_user():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    user, password = make_user(hasher=hasher, is_active=False)
    user_repo.save(user)

    changer = PasswordChanger(user_repo, hasher, FakeInvalidateCache())
    with pytest.raises(PermissionError):
        changer.run(user.id.value, password, "NewSecret123!")


def test_user_toggler_success():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    cache = FakeInvalidateCache()
    user, _ = make_user(hasher=hasher)
    user_repo.save(user)

    toggler = UserToggler(user_repo, cache)
    toggler.run(user.id.value)

    updated = user_repo.find_by_id(user.id)
    assert updated.is_active.value is False
    assert cache.calls == 1


def test_user_toggler_not_found():
    toggler = UserToggler(FakeUserRepository(), FakeInvalidateCache())
    with pytest.raises(UserNotFoundError):
        toggler.run(str(uuid4()))


def test_user_updater_success():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    cache = FakeInvalidateCache()

    role = make_role("admin")
    role_repo.add(role)
    user, _ = make_user(hasher=hasher, role_id=role.id.value)
    user_repo.save(user)

    updater = UserUpdater(user_repo, role_repo, hasher, cache)
    updater.run(user.id.value, name="Updated", email="updated@example.com", role_id=role.id.value)

    updated = user_repo.find_by_id(user.id)
    assert updated.name.value == "Updated"
    assert updated.email.value == "updated@example.com"
    assert cache.calls == 1


def test_user_updater_not_found():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    cache = FakeInvalidateCache()

    updater = UserUpdater(user_repo, role_repo, hasher, cache)
    with pytest.raises(UserNotFoundError):
        updater.run(str(uuid4()), name="Updated")


def test_user_updater_invalid_role():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    cache = FakeInvalidateCache()

    user, _ = make_user(hasher=hasher)
    user_repo.save(user)

    updater = UserUpdater(user_repo, role_repo, hasher, cache)
    with pytest.raises(ValueError):
        updater.run(user.id.value, role_id=str(uuid4()))


def test_user_updater_with_password():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    cache = FakeInvalidateCache()

    role = make_role("admin")
    role_repo.add(role)
    user, _ = make_user(hasher=hasher, role_id=role.id.value)
    user_repo.save(user)

    updater = UserUpdater(user_repo, role_repo, hasher, cache)
    updater.run(user.id.value, password="NewPass123!")

    updated = user_repo.find_by_id(user.id)
    assert updated.password.value == "hashed::NewPass123!"


def test_create_user_command_handler():
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    hasher = FakePasswordHasher()
    cache = FakeInvalidateCache()
    role = make_role("admin")
    role_repo.add(role)
    handler = CreateUserCommandHandler(UserCreator(user_repo, role_repo, hasher, cache))
    uid = str(uuid4())
    cmd = CreateUserCommand(id=uid, name="Alice", email="alice@example.com", password="Secret123!", role_name="admin")
    handler.handle(cmd)
    assert user_repo.find_by_id(IdValueObject(uid)) is not None


def test_change_password_command_handler():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    user, password = make_user(hasher=hasher)
    user_repo.save(user)

    handler = ChangePasswordCommandHandler(PasswordChanger(user_repo, hasher, FakeInvalidateCache()))
    cmd = ChangePasswordCommand(user_id=user.id.value, current_password=password, new_password="NewSecret123!")
    handler.handle(cmd)
    assert user_repo.find_by_id(user.id).password.value == "hashed::NewSecret123!"


def test_toggle_user_command_handler():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    user, _ = make_user(hasher=hasher)
    user_repo.save(user)

    handler = ToggleUserCommandHandler(UserToggler(user_repo, FakeInvalidateCache()))
    cmd = ToggleUserCommand(id=user.id.value)
    handler.handle(cmd)
    assert user_repo.find_by_id(user.id).is_active.value is False


def test_update_user_command_handler():
    hasher = FakePasswordHasher()
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    role = make_role("admin")
    role_repo.add(role)
    user, _ = make_user(hasher=hasher, role_id=role.id.value)
    user_repo.save(user)

    handler = UpdateUserCommandHandler(UserUpdater(user_repo, role_repo, hasher, FakeInvalidateCache()))
    cmd = UpdateUserCommand(id=user.id.value, name="Updated")
    handler.handle(cmd)
    assert user_repo.find_by_id(user.id).name.value == "Updated"
