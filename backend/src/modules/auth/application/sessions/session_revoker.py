from modules.auth.domain.session_repository import SessionRepository


class SessionRevoker:
    def __init__(self, session_repository: SessionRepository) -> None:
        self._session_repository = session_repository

    def revoke_by_id(self, session_id: str) -> None:
        self._session_repository.delete_by_id(session_id)

    def revoke_by_refresh_hash(self, refresh_token_hash: str) -> None:
        self._session_repository.delete_by_refresh_hash(refresh_token_hash)
