from modules.shared.domain.command_handler import CommandHandler

from .event_publisher import EventPublisher
from .publish_event_command import PublishEventCommand


class PublishEventCommandHandler(CommandHandler):
    def __init__(self, publisher: EventPublisher) -> None:
        self._publisher = publisher

    def subscribed_to(self):
        return PublishEventCommand

    def handle(self, command: PublishEventCommand) -> None:
        self._publisher.run(
            id=command.id,
            actor_user_id=command.actor_user_id,
            actor_role=command.actor_role,
        )
