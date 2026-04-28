from abc import ABC, abstractmethod
from typing import Type, TypeVar

from .command import Command

C = TypeVar("C", bound=Command)


class CommandHandler(ABC):
    @abstractmethod
    def subscribed_to(self) -> Type[C]:
        pass

    @abstractmethod
    def handle(self, command: C) -> None:
        pass
