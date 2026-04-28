from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .role_view_dto import RoleView


class RoleViewRepository(ABC):
    @abstractmethod
    def list_all(self) -> List[RoleView]: ...

    @abstractmethod
    def invalidate_cache(self) -> None: ...
