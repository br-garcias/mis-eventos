from .value_object import ValueObject


class BoolValueObject(ValueObject):
    def __init__(self, value: bool) -> None:
        super().__init__(value)

    @property
    def value(self) -> bool:
        return self._value
