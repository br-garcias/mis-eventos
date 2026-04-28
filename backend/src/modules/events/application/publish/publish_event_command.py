from dataclasses import dataclass

from modules.shared.domain.command import Command


@dataclass(frozen=True)
class PublishEventCommand(Command):
    id: str
    actor_user_id: str
    actor_role: str
