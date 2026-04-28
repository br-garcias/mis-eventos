from dataclasses import dataclass
from datetime import datetime

from modules.shared.domain.command import Command


@dataclass(frozen=True)
class CreateEventSessionCommand(Command):
    id: str
    event_id: str
    title: str
    description: str
    speaker_name: str
    speaker_bio: str
    start_at: datetime
    end_at: datetime
