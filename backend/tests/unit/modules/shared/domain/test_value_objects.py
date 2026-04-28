"""Unit tests for shared domain value objects."""
from datetime import datetime

import pytest

from modules.shared.domain.value_object.date_value_object import DateValueObject
from modules.shared.domain.value_object.enum_value_object import EnumValueObject
from modules.shared.domain.value_object.number_value_object import NumberValueObject
from modules.shared.domain.value_object.value_object import ValueObject
from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError


class FakeValueObject(ValueObject):
    def _ensure_valid(self):
        if self._value == "invalid":
            raise InvalidArgumentError("Value is invalid")


class FakeEnumValueObject(EnumValueObject):
    pass


def test_value_object_eq_and_hash():
    a = FakeValueObject("hello")
    b = FakeValueObject("hello")
    c = FakeValueObject("world")
    assert a == b
    assert a != c
    assert hash(a) == hash(b)


def test_value_object_repr_and_str():
    a = FakeValueObject("hello")
    assert "hello" in repr(a)
    assert str(a) == "hello"


def test_value_object_none_raises():
    with pytest.raises(InvalidArgumentError):
        FakeValueObject(None)


def test_value_object_ensure_valid_raises():
    with pytest.raises(InvalidArgumentError):
        FakeValueObject("invalid")


def test_value_object_different_class_eq():
    a = FakeValueObject("hello")
    assert a != "hello"


def test_date_value_object():
    now = datetime.now()
    d = DateValueObject(now)
    assert d.value == now


def test_enum_value_object_valid():
    e = FakeEnumValueObject("a", ["a", "b", "c"])
    assert e.value == "a"


def test_enum_value_object_invalid():
    with pytest.raises(InvalidArgumentError) as exc:
        FakeEnumValueObject("z", ["a", "b", "c"])
    assert "does not allow the value" in str(exc.value)


def test_number_value_object():
    n = NumberValueObject(42)
    assert n.value == 42
    m = NumberValueObject(10)
    assert n.is_bigger_than(m)
    assert not m.is_bigger_than(n)
