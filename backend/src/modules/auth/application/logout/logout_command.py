from dataclasses import dataclass
from modules.shared.domain.command import Command


@dataclass(frozen=True)
class LogoutCommand(Command):
    session_id: str
