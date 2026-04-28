from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError
from modules.shared.domain.value_object.string_value_object import StringValueObject


class SessionDescription(StringValueObject):
    MAX_LENGTH = 5000

    def _ensure_valid(self) -> None:
        v = self._value
        if not isinstance(v, str):
            raise InvalidArgumentError("SessionDescription must be a string")
        if len(v) > self.MAX_LENGTH:
            raise InvalidArgumentError(
                f"SessionDescription must be at most {self.MAX_LENGTH} characters"
            )
