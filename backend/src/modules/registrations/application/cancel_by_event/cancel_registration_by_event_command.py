from dataclasses import dataclass

from modules.shared.domain.command import Command


@dataclass(frozen=True)
class CancelRegistrationByEventCommand(Command):
    user_id: str
    event_id: str
