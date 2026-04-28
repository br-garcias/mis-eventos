from dataclasses import dataclass

from modules.shared.domain.query import Query


@dataclass(frozen=True)
class SearchUsersQuery(Query):
    email: str | None = None
    name: str | None = None
    role_id: str | None = None
    page: int = 1
    size: int = 10
