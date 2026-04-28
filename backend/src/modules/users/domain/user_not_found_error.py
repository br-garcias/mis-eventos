from modules.shared.domain.domain_error import NotFoundError


class UserNotFoundError(NotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"User <{identifier}> not found")
