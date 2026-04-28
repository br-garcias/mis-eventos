from modules.shared.domain.command_handler import CommandHandler

from .register_to_event_command import RegisterToEventCommand
from .register_to_event_service import RegisterToEventService


class RegisterToEventCommandHandler(CommandHandler):
    def __init__(self, service: RegisterToEventService) -> None:
        self._service = service

    def subscribed_to(self):
        return RegisterToEventCommand

    def handle(self, command: RegisterToEventCommand) -> None:
        self._service.run(
            registration_id=command.registration_id,
            event_id=command.event_id,
            user_id=command.user_id,
        )
