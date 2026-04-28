"""Unit tests for User Views query handlers."""
from uuid import uuid4

from modules.user_views.application.find_by_id.find_user_by_id_query import FindUserByIdQuery
from modules.user_views.application.find_by_id.find_user_by_id_query_handler import FindUserByIdQueryHandler
from modules.user_views.application.find_by_id.user_finder_by_id import UserFinderById
from modules.user_views.application.search.search_users_query import SearchUsersQuery
from modules.user_views.application.search.search_users_query_handler import SearchUsersQueryHandler
from modules.user_views.application.search.user_searcher import UserSearcher
from modules.user_views.domain.user_view_dto import RoleView, UserDetailView, UserSummaryView
from modules.user_views.domain.user_view_repository import UserViewRepository


class FakeUserViewRepository(UserViewRepository):
    def __init__(self) -> None:
        self._users: dict[str, UserDetailView] = {}

    def add(self, user: UserDetailView) -> None:
        self._users[user.id] = user

    def search(self, *, email=None, name=None, role_id=None, page=1, size=20) -> tuple[list[UserSummaryView], int]:
        results = list(self._users.values())
        if email:
            results = [u for u in results if email.lower() in u.email.lower()]
        if name:
            results = [u for u in results if name.lower() in u.name.lower()]
        if role_id:
            results = [u for u in results if u.role.id == role_id]
        total = len(results)
        skip = (page - 1) * size
        items = [
            UserSummaryView(
                id=u.id,
                name=u.name,
                email=u.email,
                is_active=u.is_active,
                created_at=u.created_at,
                updated_at=u.updated_at,
                role=u.role,
            )
            for u in results[skip : skip + size]
        ]
        return items, total

    def find_by_id(self, id: str) -> UserDetailView | None:
        return self._users.get(id)

    def invalidate_cache(self) -> None:
        pass


def _make_detail():
    role = RoleView(id=str(uuid4()), name="admin")
    return UserDetailView(
        id=str(uuid4()),
        name="Alice",
        email="alice@example.com",
        is_active=True,
        created_at="2025-10-14T15:50:00.000000Z",
        updated_at="2025-10-14T15:50:00.000000Z",
        role=role,
    )


def test_find_user_by_id_query_handler():
    repo = FakeUserViewRepository()
    user = _make_detail()
    repo.add(user)

    finder = UserFinderById(repo)
    handler = FindUserByIdQueryHandler(finder)

    result = handler.handle(FindUserByIdQuery(id=user.id))
    assert result is not None
    assert result.name == "Alice"
    assert handler.subscribed_to() == FindUserByIdQuery


def test_search_users_query_handler():
    repo = FakeUserViewRepository()
    user = _make_detail()
    repo.add(user)

    searcher = UserSearcher(repo)
    handler = SearchUsersQueryHandler(searcher)

    result = handler.handle(SearchUsersQuery())
    assert result.total == 1
    assert result.items[0].name == "Alice"
    assert result.page == 1
    assert result.size == 10
    assert handler.subscribed_to() == SearchUsersQuery


def test_user_detail_view_to_primitive():
    role = RoleView(id="r1", name="admin")
    user = UserDetailView(
        id="u1",
        name="Alice",
        email="a@e.com",
        is_active=True,
        created_at="2025-10-14T15:50:00.000000Z",
        updated_at="2025-10-14T15:50:00.000000Z",
        role=role,
    )
    d = user.to_primitive()
    assert d["id"] == "u1"
    assert d["role"]["role"] == "admin"


def test_user_detail_view_from_primitive():
    d = {
        "id": "u1",
        "name": "Alice",
        "email": "a@e.com",
        "is_active": True,
        "created_at": "2025-10-14T15:50:00.000000Z",
        "updated_at": "2025-10-14T15:50:00.000000Z",
        "role": {"id": "r1", "role": "admin"},
    }
    user = UserDetailView.from_primitive(d)
    assert user.name == "Alice"
    assert user.role.name == "admin"


def test_user_summary_view_to_primitive():
    role = RoleView(id="r1", name="admin")
    user = UserSummaryView(
        id="u1",
        name="Alice",
        email="a@e.com",
        is_active=True,
        created_at="2025-10-14T15:50:00.000000Z",
        updated_at="2025-10-14T15:50:00.000000Z",
        role=role,
    )
    d = user.to_primitive()
    assert d["id"] == "u1"


def test_user_summary_view_from_primitive():
    d = {
        "id": "u1",
        "name": "Alice",
        "email": "a@e.com",
        "is_active": True,
        "created_at": "2025-10-14T15:50:00.000000Z",
        "updated_at": "2025-10-14T15:50:00.000000Z",
        "role": {"id": "r1", "role": "admin"},
    }
    user = UserSummaryView.from_primitive(d)
    assert user.email == "a@e.com"
