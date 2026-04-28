from dataclasses import dataclass
from modules.shared.domain.command import Command


@dataclass(frozen=True)
class CreateUserCommand(Command):
    id: str
    name: str
    email: str
    password: str
    role_name: str
