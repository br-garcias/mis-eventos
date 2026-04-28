from modules.shared.domain.domain_error import NotFoundError


class SessionNotFoundError(NotFoundError):
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Session <{session_id}> not found")
