from abc import ABC, abstractmethod
from typing import Any
from .query import Query


class QueryBus(ABC):
    @abstractmethod
    def ask(self, query: Query) -> Any:
        pass
