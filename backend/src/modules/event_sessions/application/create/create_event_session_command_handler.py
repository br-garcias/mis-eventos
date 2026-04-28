from modules.shared.domain.command_handler import CommandHandler

from .create_event_session_command import CreateEventSessionCommand
from .event_session_creator import EventSessionCreator


class CreateEventSessionCommandHandler(CommandHandler):
    def __init__(self, creator: EventSessionCreator) -> None:
        self._creator = creator

    def subscribed_to(self):
        return CreateEventSessionCommand

    def handle(self, command: CreateEventSessionCommand) -> None:
        self._creator.run(
            id=command.id,
            event_id=command.event_id,
            title=command.title,
            description=command.description,
            speaker_name=command.speaker_name,
            speaker_bio=command.speaker_bio,
            start_at=command.start_at,
            end_at=command.end_at,
        )
