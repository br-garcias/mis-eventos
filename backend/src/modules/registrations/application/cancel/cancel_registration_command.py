from dataclasses import dataclass

from modules.shared.domain.command import Command


@dataclass(frozen=True)
class CancelRegistrationCommand(Command):
    registration_id: str
    user_id: str
