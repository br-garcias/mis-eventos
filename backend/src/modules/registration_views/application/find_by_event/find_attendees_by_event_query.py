from dataclasses import dataclass

from modules.shared.domain.query import Query


@dataclass(frozen=True)
class FindAttendeesByEventQuery(Query):
    event_id: str
    actor_user_id: str
    actor_role: str
