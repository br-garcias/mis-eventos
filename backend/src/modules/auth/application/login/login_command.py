from dataclasses import dataclass
from modules.shared.domain.command import Command

@dataclass(frozen=True)
class LoginCommand(Command):
    email: str
    password: str
    ip_address: str
