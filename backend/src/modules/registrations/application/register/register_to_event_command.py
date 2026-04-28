from dataclasses import dataclass

from modules.shared.domain.command import Command


@dataclass(frozen=True)
class RegisterToEventCommand(Command):
    registration_id: str
    event_id: str
    user_id: str
