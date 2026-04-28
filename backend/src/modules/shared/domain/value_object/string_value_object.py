from .value_object import ValueObject


class StringValueObject(ValueObject):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    @property
    def value(self) -> str:
        return self._value
