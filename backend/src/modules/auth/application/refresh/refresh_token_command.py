from dataclasses import dataclass
from modules.shared.domain.command import Command

@dataclass(frozen=True)
class RefreshTokenCommand(Command):
    refresh_token: str
    ip_address: str
