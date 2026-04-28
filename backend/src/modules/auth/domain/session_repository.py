from abc import ABC, abstractmethod

from .session import Session


class SessionRepository(ABC):
    @abstractmethod
    def save(self, session: Session) -> None: ...

    @abstractmethod
    def find_by_refresh_hash(self, refresh_token_hash: str) -> Session | None: ...

    @abstractmethod
    def delete_by_refresh_hash(self, refresh_token_hash: str) -> None: ...

    @abstractmethod
    def find_by_id(self, session_id: str) -> Session | None: ...

    @abstractmethod
    def delete_by_id(self, session_id: str) -> None: ...
