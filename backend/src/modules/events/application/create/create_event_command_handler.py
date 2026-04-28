from modules.shared.domain.command_handler import CommandHandler

from .create_event_command import CreateEventCommand
from .event_creator import EventCreator


class CreateEventCommandHandler(CommandHandler):
    def __init__(self, creator: EventCreator) -> None:
        self._creator = creator

    def subscribed_to(self):
        return CreateEventCommand

    def handle(self, command: CreateEventCommand) -> None:
        self._creator.run(
            id=command.id,
            name=command.name,
            description=command.description,
            organizer_id=command.organizer_id,
            capacity=command.capacity,
            start_at=command.start_at,
            end_at=command.end_at,
            location=command.location,
        )
