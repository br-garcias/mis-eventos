from typing import Any, Callable, Dict, Type

from modules.shared.domain.command import Command
from modules.users.application.change_password.change_password_command import ChangePasswordCommand
from modules.users.application.change_password.change_password_command_handler import (
    ChangePasswordCommandHandler,
)
from modules.users.application.change_password.password_changer import PasswordChanger
from modules.users.application.create.create_user_command import CreateUserCommand
from modules.users.application.create.create_user_command_handler import CreateUserCommandHandler
from modules.users.application.create.user_creator import UserCreator
from modules.users.application.toggle.toggle_user_command import ToggleUserCommand
from modules.users.application.toggle.toggle_user_command_handler import ToggleUserCommandHandler
from modules.users.application.toggle.user_toggler import UserToggler
from modules.users.application.update.update_user_command import UpdateUserCommand
from modules.users.application.update.update_user_command_handler import UpdateUserCommandHandler
from modules.users.application.update.user_updater import UserUpdater
from modules.users.domain.user_repository import UserRepository
from modules.users.infrastructure.persistence.mongo_user_repository import MongoUserRepository

from .shared_di import mongo_client
from .roles_di import role_repository
from .shared_di import password_hasher
from .user_views_di import user_view_cache_invalidator

user_repository: UserRepository = MongoUserRepository(mongo_client)


def users_command_handlers() -> Dict[Type[Command], Callable[[Command], Any]]:
    user_creator     = UserCreator(user_repository, role_repository, password_hasher, user_view_cache_invalidator)
    user_updater     = UserUpdater(user_repository, role_repository, password_hasher, user_view_cache_invalidator)
    user_toggler     = UserToggler(user_repository, user_view_cache_invalidator)
    password_changer = PasswordChanger(user_repository, password_hasher, user_view_cache_invalidator)

    return {
        CreateUserCommand:     CreateUserCommandHandler(user_creator),
        UpdateUserCommand:     UpdateUserCommandHandler(user_updater),
        ToggleUserCommand:     ToggleUserCommandHandler(user_toggler),
        ChangePasswordCommand: ChangePasswordCommandHandler(password_changer),
    }
