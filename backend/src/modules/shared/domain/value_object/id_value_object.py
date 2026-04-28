import uuid

from .invalid_argument_error import InvalidArgumentError
from .string_value_object import StringValueObject


class IdValueObject(StringValueObject):
    def __init__(self, value: str) -> None:
        super().__init__(value)
        self._ensure_is_valid_uuid(value)

    @staticmethod
    def random() -> "IdValueObject":
        return IdValueObject(str(uuid.uuid4()))

    def _ensure_is_valid_uuid(self, id_value: str) -> None:
        try:
            uuid.UUID(id_value)
        except ValueError:
            raise InvalidArgumentError(
                f"<{self.__class__.__name__}> does not allow the value <{id_value}>"
            )
