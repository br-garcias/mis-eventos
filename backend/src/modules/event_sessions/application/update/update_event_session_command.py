from dataclasses import dataclass
from datetime import datetime

from modules.shared.domain.command import Command


@dataclass(frozen=True)
class UpdateEventSessionCommand(Command):
    id: str
    title: str | None = None
    description: str | None = None
    speaker_name: str | None = None
    speaker_bio: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
