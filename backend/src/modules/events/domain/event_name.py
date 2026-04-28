from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError
from modules.shared.domain.value_object.string_value_object import StringValueObject


class EventName(StringValueObject):
    
    MIN_LENGTH = 3
    MAX_LENGTH = 200

    def _ensure_valid(self) -> None:
        v = self._value
        if not isinstance(v, str):
            raise InvalidArgumentError("EventName must be a string")
        cleaned = v.strip()
        if len(cleaned) < self.MIN_LENGTH:
            raise InvalidArgumentError(
                f"EventName must have at least {self.MIN_LENGTH} characters"
            )
        if len(cleaned) > self.MAX_LENGTH:
            raise InvalidArgumentError(
                f"EventName must have at most {self.MAX_LENGTH} characters"
            )
        self._value = cleaned
