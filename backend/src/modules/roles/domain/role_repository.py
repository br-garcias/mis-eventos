from abc import ABC, abstractmethod
from .role import Role


class RoleRepository(ABC):
    @abstractmethod
    def find_by_name(self, name: str) -> Role | None: ...

    @abstractmethod
    def find_by_id(self, id: str) -> Role | None: ...
