from typing import List

from modules.role_views.application.list_roles.role_lister import RoleLister
from modules.role_views.domain.role_view_dto import RoleView
from modules.role_views.domain.role_view_repository import RoleViewRepository


class FakeRoleViewRepository(RoleViewRepository):
    def __init__(self, rows: List[RoleView]) -> None:
        self._rows = rows

    def list_all(self) -> List[RoleView]:
        return self._rows

    def invalidate_cache(self) -> None:
        pass


def test_returns_empty_list_when_no_roles():
    repo = FakeRoleViewRepository([])
    lister = RoleLister(repo)

    result = lister.run()

    assert result == []


def test_returns_all_roles():
    rows = [
        RoleView(id="r-1", name="admin", created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z"),
        RoleView(id="r-2", name="attendee", created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z"),
        RoleView(id="r-3", name="organizer", created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z"),
    ]
    repo = FakeRoleViewRepository(rows)
    lister = RoleLister(repo)

    result = lister.run()

    assert len(result) == 3
    assert [r.name for r in result] == ["admin", "attendee", "organizer"]
