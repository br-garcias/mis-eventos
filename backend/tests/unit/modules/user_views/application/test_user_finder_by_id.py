from modules.user_views.application.find_by_id.user_finder_by_id import UserFinderById
from modules.user_views.domain.user_view_dto import RoleView, UserDetailView
from modules.user_views.domain.user_view_repository import UserViewRepository


class FakeUserViewRepository(UserViewRepository):
    def __init__(self, store: dict[str, UserDetailView]) -> None:
        self._store = store

    def search(self, *, email=None, name=None, role_id=None, page=1, size=20):
        return [], 0

    def find_by_id(self, id):
        return self._store.get(id)

    def invalidate_cache(self) -> None:
        pass


def _detail(id: str) -> UserDetailView:
    return UserDetailView(
        id=id,
        name="Alice",
        email="alice@x.com",
        is_active=True,
        created_at="2025-10-14T15:50:00.000000Z",
        updated_at="2025-10-14T15:50:00.000000Z",
        role=RoleView(id="r-1", name="admin"),
    )


def test_returns_user_with_role():
    repo = FakeUserViewRepository({"u-1": _detail("u-1")})
    finder = UserFinderById(repo)

    result = finder.run("u-1")

    assert result is not None
    assert result.email == "alice@x.com"
    assert result.role.name == "admin"


def test_returns_none_when_missing():
    repo = FakeUserViewRepository({})
    finder = UserFinderById(repo)

    assert finder.run("ghost") is None
