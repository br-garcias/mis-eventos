from dataclasses import dataclass
from modules.shared.domain.command import Command


@dataclass(frozen=True)
class ChangePasswordCommand(Command):
    user_id: str
    current_password: str
    new_password: str
