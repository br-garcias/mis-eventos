from modules.shared.domain.command_handler import CommandHandler

from .event_updater import EventUpdater
from .update_event_command import UpdateEventCommand


class UpdateEventCommandHandler(CommandHandler):
    def __init__(self, updater: EventUpdater) -> None:
        self._updater = updater

    def subscribed_to(self):
        return UpdateEventCommand

    def handle(self, command: UpdateEventCommand) -> None:
        self._updater.run(
            id=command.id,
            actor_user_id=command.actor_user_id,
            actor_role=command.actor_role,
            name=command.name,
            description=command.description,
            location=command.location,
            start_at=command.start_at,
            end_at=command.end_at,
            capacity=command.capacity,
        )
