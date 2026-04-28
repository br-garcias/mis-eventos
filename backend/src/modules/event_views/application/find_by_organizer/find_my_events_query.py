from dataclasses import dataclass

from modules.shared.domain.query import Query


@dataclass(frozen=True)
class FindMyEventsQuery(Query):
    organizer_id: str
    q: str | None = None
    status: str | None = None
    page: int = 1
    size: int = 20
