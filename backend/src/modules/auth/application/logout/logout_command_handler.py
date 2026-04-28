from modules.shared.domain.command_handler import CommandHandler

from .logout_command import LogoutCommand
from .user_logout import UserLogout


class LogoutCommandHandler(CommandHandler):
    def __init__(self, user_logout: UserLogout) -> None:
        self._user_logout = user_logout

    def subscribed_to(self):
        return LogoutCommand

    def handle(self, command: LogoutCommand) -> None:
        self._user_logout.logout(command.session_id)
