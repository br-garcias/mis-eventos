from dataclasses import dataclass
from modules.shared.domain.command import Command


@dataclass(frozen=True)
class ToggleUserCommand(Command):
    id: str
