from modules.auth.application.sessions.session_revoker import SessionRevoker


class UserLogout:
    def __init__(self, session_revoker: SessionRevoker) -> None:
        self._session_revoker = session_revoker

    def logout(self, session_id: str) -> None:
        self._session_revoker.revoke_by_id(session_id)
