from modules.auth.application.auth_response import AuthResponse
from modules.shared.domain.command_handler import CommandHandler

from .refresh_token_command import RefreshTokenCommand
from .session_renewer import SessionRenewer


class RefreshTokenCommandHandler(CommandHandler):
    def __init__(self, renewer: SessionRenewer) -> None:
        self._renewer = renewer

    def subscribed_to(self):
        return RefreshTokenCommand

    def handle(self, command: RefreshTokenCommand) -> AuthResponse:
        return self._renewer.renew(command.refresh_token, command.ip_address)
