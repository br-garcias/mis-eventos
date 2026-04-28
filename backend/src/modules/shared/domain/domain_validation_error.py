from modules.shared.domain.domain_error import ValidationError


class DomainValidationError(ValidationError):
    def __init__(self, errors: dict[str, list[str]]) -> None:
        self.errors = errors
        super().__init__(f"Domain validation failed: {errors}")
