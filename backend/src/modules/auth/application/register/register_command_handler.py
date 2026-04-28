from modules.auth.application.auth_response import AuthResponse
from modules.shared.domain.command_handler import CommandHandler

from .attendee_registrar import AttendeeRegistrar
from .register_command import RegisterCommand


class RegisterCommandHandler(CommandHandler):
    def __init__(self, registrar: AttendeeRegistrar) -> None:
        self._registrar = registrar

    def subscribed_to(self):
        return RegisterCommand

    def handle(self, command: RegisterCommand) -> AuthResponse:
        return self._registrar.register(
            name=command.name,
            email=command.email,
            password=command.password,
            ip_address=command.ip_address,
        )
