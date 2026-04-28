from dataclasses import dataclass
from modules.shared.domain.query import Query


@dataclass(frozen=True)
class ValidateTokenQuery(Query):
    token: str
