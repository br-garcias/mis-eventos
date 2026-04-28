from abc import ABC
from typing import Any

from .invalid_argument_error import InvalidArgumentError


class ValueObject(ABC):
    def __init__(self, value: Any) -> None:
        self._value = value
        self._ensure_value_is_defined(value)
        self._ensure_valid()

    def _ensure_valid(self) -> None:
        pass

    @property
    def value(self) -> Any:
        return self._value

    def _ensure_value_is_defined(self, value: Any) -> None:
        if value is None:
            raise InvalidArgumentError("Value must be defined")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(value={self._value!r})>"

    def __str__(self) -> str:
        return str(self._value)
