from modules.shared.domain.command_handler import CommandHandler

from .cancel_registration_by_event_command import CancelRegistrationByEventCommand
from .cancel_registration_by_event_service import CancelRegistrationByEventService


class CancelRegistrationByEventCommandHandler(CommandHandler):
    def __init__(self, service: CancelRegistrationByEventService) -> None:
        self._service = service

    def subscribed_to(self):
        return CancelRegistrationByEventCommand

    def handle(self, command: CancelRegistrationByEventCommand) -> None:
        self._service.run(
            event_id=command.event_id,
            user_id=command.user_id,
        )
