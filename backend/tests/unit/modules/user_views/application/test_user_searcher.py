from datetime import datetime

from modules.user_views.application.search.user_searcher import UserSearcher
from modules.user_views.domain.user_view_dto import RoleView, UserSummaryView
from modules.user_views.domain.user_view_repository import UserViewRepository


class FakeUserViewRepository(UserViewRepository):
    def __init__(self, rows: list[UserSummaryView]) -> None:
        self._rows = rows
        self.last_call: dict | None = None

    def search(self, *, email=None, name=None, role_id=None, page=1, size=20):
        self.last_call = {"email": email, "name": name, "role_id": role_id, "page": page, "size": size}
        result = self._rows
        if email is not None:
            result = [r for r in result if email.lower() in r.email.lower()]
        if name is not None:
            result = [r for r in result if name.lower() in r.name.lower()]
        if role_id is not None:
            result = [r for r in result if r.role.id == role_id]
        total = len(result)
        skip = (page - 1) * size
        return result[skip : skip + size], total

    def find_by_id(self, id):  # not used in this test
        return None

    def invalidate_cache(self) -> None:
        pass


def _row(email: str, role_id: str = "r-1") -> UserSummaryView:
    return UserSummaryView(
        id=f"u-{email}",
        name="X",
        email=email,
        is_active=True,
        created_at="2025-10-14T15:50:00.000000Z",
        updated_at="2025-10-14T15:50:00.000000Z",
        role=RoleView(id=role_id, name="admin"),
    )


def test_returns_all_when_no_filters():
    repo = FakeUserViewRepository([_row("a@x.com"), _row("b@x.com", role_id="r-2")])
    searcher = UserSearcher(repo)

    items, total = searcher.run()
    assert total == 2
    assert len(items) == 2
    assert repo.last_call == {"email": None, "name": None, "role_id": None, "page": 1, "size": 20}


def test_filters_by_email():
    repo = FakeUserViewRepository([_row("a@x.com"), _row("b@x.com")])
    searcher = UserSearcher(repo)

    items, total = searcher.run(email="b@x.com")

    assert [r.email for r in items] == ["b@x.com"]


def test_filters_by_role_id():
    repo = FakeUserViewRepository([_row("a@x.com"), _row("b@x.com", role_id="r-2")])
    searcher = UserSearcher(repo)

    items, total = searcher.run(role_id="r-2")

    assert [r.email for r in items] == ["b@x.com"]


def test_combines_filters():
    repo = FakeUserViewRepository([
        _row("a@x.com"),
        _row("b@x.com", role_id="r-2"),
        _row("c@x.com", role_id="r-2"),
    ])
    searcher = UserSearcher(repo)

    items, total = searcher.run(email="c@x.com", role_id="r-2")

    assert [r.email for r in items] == ["c@x.com"]
