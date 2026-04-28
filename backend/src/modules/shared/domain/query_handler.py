from abc import ABC, abstractmethod
from typing import Type, TypeVar

from .query import Query
from .response import Response

Q = TypeVar("Q", bound=Query)
R = TypeVar("R", bound=Response)


class QueryHandler(ABC):
    @abstractmethod
    def subscribed_to(self) -> Type[Q]:
        pass

    @abstractmethod
    def handle(self, query: Q) -> R:
        pass
