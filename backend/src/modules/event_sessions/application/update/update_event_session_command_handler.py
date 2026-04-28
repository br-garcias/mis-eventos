from modules.shared.domain.command_handler import CommandHandler

from .event_session_updater import EventSessionUpdater
from .update_event_session_command import UpdateEventSessionCommand


class UpdateEventSessionCommandHandler(CommandHandler):
    def __init__(self, updater: EventSessionUpdater) -> None:
        self._updater = updater

    def subscribed_to(self):
        return UpdateEventSessionCommand

    def handle(self, command: UpdateEventSessionCommand) -> None:
        self._updater.run(
            id=command.id,
            title=command.title,
            description=command.description,
            speaker_name=command.speaker_name,
            speaker_bio=command.speaker_bio,
            start_at=command.start_at,
            end_at=command.end_at,
        )
