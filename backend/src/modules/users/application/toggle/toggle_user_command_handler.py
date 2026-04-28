from modules.shared.domain.command_handler import CommandHandler
from .toggle_user_command import ToggleUserCommand
from .user_toggler import UserToggler


class ToggleUserCommandHandler(CommandHandler):
    def __init__(self, toggler: UserToggler) -> None:
        self._toggler = toggler

    def subscribed_to(self):
        return ToggleUserCommand

    def handle(self, command: ToggleUserCommand) -> None:
        self._toggler.run(command.id)
