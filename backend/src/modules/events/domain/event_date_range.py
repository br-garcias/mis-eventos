from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError


@dataclass(frozen=True)
class EventDateRange:

    start_at: datetime
    end_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.start_at, datetime) or not isinstance(self.end_at, datetime):
            raise InvalidArgumentError("EventDateRange requires datetime instances")
        if self.start_at >= self.end_at:
            raise InvalidArgumentError("EventDateRange start_at must be strictly before end_at")

    def contains(self, other: "EventDateRange") -> bool:
        return self.start_at <= other.start_at and other.end_at <= self.end_at

    def overlaps(self, other: "EventDateRange") -> bool:
        return self.start_at < other.end_at and other.start_at < self.end_at
