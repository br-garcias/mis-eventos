from modules.shared.domain.command_handler import CommandHandler

from .cancel_registration_command import CancelRegistrationCommand
from .cancel_registration_service import CancelRegistrationService


class CancelRegistrationCommandHandler(CommandHandler):
    def __init__(self, service: CancelRegistrationService) -> None:
        self._service = service

    def subscribed_to(self):
        return CancelRegistrationCommand

    def handle(self, command: CancelRegistrationCommand) -> None:
        self._service.run(
            registration_id=command.registration_id,
            user_id=command.user_id,
        )
