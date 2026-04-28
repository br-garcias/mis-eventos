from dataclasses import dataclass

from modules.shared.domain.query import Query


@dataclass(frozen=True)
class FindEventByIdQuery(Query):
    id: str
    user_id: str | None = None
