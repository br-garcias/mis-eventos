from abc import ABC, abstractmethod

from modules.shared.domain.value_object.id_value_object import IdValueObject
from .user import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None: ...

    @abstractmethod
    def find_by_id(self, id: IdValueObject) -> User | None: ...

    @abstractmethod
    def find_by_email(self, email: str) -> User | None: ...
