from modules.shared.domain.value_object import StringValueObject, InvalidArgumentError


class UserName(StringValueObject):
    MIN_LENGTH = 1
    MAX_LENGTH = 100

    def _ensure_valid(self) -> None:
        if len(self.value) < self.MIN_LENGTH:
            raise InvalidArgumentError(f"Must be at least {self.MIN_LENGTH} characters")
        if len(self.value) > self.MAX_LENGTH:
            raise InvalidArgumentError(f"Must be at most {self.MAX_LENGTH} characters")
