from modules.shared.domain.command_handler import CommandHandler

from .delete_event_session_command import DeleteEventSessionCommand
from .event_session_deleter import EventSessionDeleter


class DeleteEventSessionCommandHandler(CommandHandler):
    def __init__(self, deleter: EventSessionDeleter) -> None:
        self._deleter = deleter

    def subscribed_to(self):
        return DeleteEventSessionCommand

    def handle(self, command: DeleteEventSessionCommand) -> None:
        self._deleter.run(id=command.id)
