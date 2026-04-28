from modules.shared.domain.command_handler import CommandHandler
from .update_user_command import UpdateUserCommand
from .user_updater import UserUpdater


class UpdateUserCommandHandler(CommandHandler):
    def __init__(self, updater: UserUpdater) -> None:
        self._updater = updater

    def subscribed_to(self):
        return UpdateUserCommand

    def handle(self, command: UpdateUserCommand) -> None:
        self._updater.run(
            id=command.id,
            name=command.name,
            email=command.email,
            password=command.password,
            role_id=command.role_id,
        )
