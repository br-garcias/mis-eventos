from typing import Union

from .value_object import ValueObject


class NumberValueObject(ValueObject):
    def __init__(self, value: Union[float, int]) -> None:
        super().__init__(value)

    @property
    def value(self) -> Union[float, int]:
        return self._value

    def is_bigger_than(self, other: "NumberValueObject") -> bool:
        return self.value > other.value
