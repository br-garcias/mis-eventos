from dataclasses import dataclass
from datetime import datetime

from modules.shared.domain.query import Query


@dataclass(frozen=True)
class SearchEventsQuery(Query):
    q: str | None = None
    status: str | None = None
    organizer_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    sort_by: str = "start_at"
    page: int = 1
    size: int = 20
    user_id: str | None = None
