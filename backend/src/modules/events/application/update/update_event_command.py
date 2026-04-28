from dataclasses import dataclass
from datetime import datetime

from modules.shared.domain.command import Command


@dataclass(frozen=True)
class UpdateEventCommand(Command):
    id: str
    actor_user_id: str
    actor_role: str
    name: str | None = None
    description: str | None = None
    location: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    capacity: int | None = None
