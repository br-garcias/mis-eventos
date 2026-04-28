from modules.auth.application.auth_response import AuthResponse
from modules.shared.domain.command_handler import CommandHandler

from .login_command import LoginCommand
from .user_authenticator import UserAuthenticator


class LoginCommandHandler(CommandHandler):
    def __init__(self, authenticator: UserAuthenticator) -> None:
        self._authenticator = authenticator

    def subscribed_to(self):
        return LoginCommand

    def handle(self, command: LoginCommand) -> AuthResponse:
        return self._authenticator.authenticate(
            command.email,
            command.password,
            command.ip_address,
        )
