from modules.shared.domain.command_handler import CommandHandler
from .create_user_command import CreateUserCommand
from .user_creator import UserCreator


class CreateUserCommandHandler(CommandHandler):
    def __init__(self, creator: UserCreator) -> None:
        self._creator = creator

    def subscribed_to(self):
        return CreateUserCommand

    def handle(self, command: CreateUserCommand) -> None:
        self._creator.run(
            id=command.id,
            name=command.name,
            email=command.email,
            password=command.password,
            role_name=command.role_name,
        )
