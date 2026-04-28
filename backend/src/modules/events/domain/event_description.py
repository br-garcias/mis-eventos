from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError
from modules.shared.domain.value_object.string_value_object import StringValueObject


class EventDescription(StringValueObject):
    MAX_LENGTH = 5000

    def _ensure_valid(self) -> None:
        if not isinstance(self._value, str):
            raise InvalidArgumentError("EventDescription must be a string")
        if len(self._value) > self.MAX_LENGTH:
            raise InvalidArgumentError(
                f"EventDescription must have at most {self.MAX_LENGTH} characters"
            )
