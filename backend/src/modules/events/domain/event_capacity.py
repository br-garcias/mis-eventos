from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError
from modules.shared.domain.value_object.number_value_object import NumberValueObject


class EventCapacity(NumberValueObject):

    MAX = 1_000_000

    def __init__(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidArgumentError("EventCapacity must be an integer")
        if value <= 0:
            raise InvalidArgumentError("EventCapacity must be greater than zero")
        if value > self.MAX:
            raise InvalidArgumentError(f"EventCapacity must be at most {self.MAX}")
        super().__init__(value)
