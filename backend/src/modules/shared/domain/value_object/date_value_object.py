from datetime import datetime

from .value_object import ValueObject


class DateValueObject(ValueObject):
    def __init__(self, value: datetime) -> None:
        super().__init__(value)

    @property
    def value(self) -> datetime:
        return self._value
