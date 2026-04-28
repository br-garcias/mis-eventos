from modules.shared.domain.command_handler import CommandHandler

from .delete_event_command import DeleteEventCommand
from .event_deleter import EventDeleter


class DeleteEventCommandHandler(CommandHandler):
    def __init__(self, deleter: EventDeleter) -> None:
        self._deleter = deleter

    def subscribed_to(self):
        return DeleteEventCommand

    def handle(self, command: DeleteEventCommand) -> None:
        self._deleter.run(
            id=command.id,
            actor_user_id=command.actor_user_id,
            actor_role=command.actor_role,
        )
