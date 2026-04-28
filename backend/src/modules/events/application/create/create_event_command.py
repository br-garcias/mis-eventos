from dataclasses import dataclass
from datetime import datetime

from modules.shared.domain.command import Command


@dataclass(frozen=True)
class CreateEventCommand(Command):
    id: str
    name: str
    description: str
    organizer_id: str
    capacity: int
    start_at: datetime
    end_at: datetime
    location: str = ""
