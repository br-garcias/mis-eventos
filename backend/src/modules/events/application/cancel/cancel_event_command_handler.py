from modules.shared.domain.command_handler import CommandHandler

from .cancel_event_command import CancelEventCommand
from .event_canceller import EventCanceller


class CancelEventCommandHandler(CommandHandler):
    def __init__(self, canceller: EventCanceller) -> None:
        self._canceller = canceller

    def subscribed_to(self):
        return CancelEventCommand

    def handle(self, command: CancelEventCommand) -> None:
        self._canceller.run(
            id=command.id,
            actor_user_id=command.actor_user_id,
            actor_role=command.actor_role,
        )
