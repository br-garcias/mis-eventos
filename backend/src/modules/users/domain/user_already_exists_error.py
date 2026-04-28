from modules.shared.domain.domain_error import ConflictError


class UserAlreadyExistsError(ConflictError):
    def __init__(self, email: str) -> None:
        super().__init__(f"User with email <{email}> already exists")
