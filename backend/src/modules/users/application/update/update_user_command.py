from dataclasses import dataclass
from modules.shared.domain.command import Command


@dataclass(frozen=True)
class UpdateUserCommand(Command):
    id: str
    name: str | None = None
    email: str | None = None
    password: str | None = None
    role_id: str | None = None
