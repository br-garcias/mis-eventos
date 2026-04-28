import pytest

from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError
from modules.users.domain.user_email import UserEmail


def test_accepts_valid_email():
    assert UserEmail("alice@example.com").value == "alice@example.com"


@pytest.mark.parametrize("bad", ["", "no-at", "a@b", "a b@c.com", "@x.com", "x@.com"])
def test_rejects_invalid_email(bad):
    with pytest.raises(InvalidArgumentError):
        UserEmail(bad)
