from typing import Any, Generic, TypeVar

from .invalid_argument_error import InvalidArgumentError

T = TypeVar("T")


class EnumValueObject(Generic[T]):
    def __init__(self, value: T, valid_values: list[T]) -> None:
        self._value = value
        self._valid_values = valid_values
        self._check_value_is_valid(value)

    @property
    def value(self) -> T:
        return self._value

    def _check_value_is_valid(self, value: T) -> None:
        if value not in self._valid_values:
            self._throw_error_for_invalid_value(value)

    def _throw_error_for_invalid_value(self, value: T) -> None:
        raise InvalidArgumentError(
            f"<{self.__class__.__name__}> does not allow the value <{value}>; "
            f"allowed values are {self._valid_values}"
        )
