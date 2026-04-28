import pytest

from modules.roles.domain.role_name import RoleName


def test_admin_role_name():
    assert RoleName("admin").value == "admin"


def test_unknown_role_name_rejected():
    with pytest.raises(ValueError):
        RoleName("ceo")
