from typing import Any, Callable, Dict, Type

from apps.api.config import CACHE_TTL_SECONDS
from modules.shared.domain.query import Query
from modules.user_views.application.invalidate_cache.invalidate_user_views_cache import (
    InvalidateUserViewsCache,
)
from modules.user_views.application.find_by_id.find_user_by_id_query import FindUserByIdQuery
from modules.user_views.application.find_by_id.find_user_by_id_query_handler import (
    FindUserByIdQueryHandler,
)
from modules.user_views.application.find_by_id.user_finder_by_id import UserFinderById
from modules.user_views.application.search.search_users_query import SearchUsersQuery
from modules.user_views.application.search.search_users_query_handler import SearchUsersQueryHandler
from modules.user_views.application.search.user_searcher import UserSearcher
from modules.user_views.domain.user_view_repository import UserViewRepository
from modules.user_views.infrastructure.persistence.cached_user_view_repository import (
    CachedUserViewRepository,
)
from modules.user_views.infrastructure.persistence.mongo_user_view_repository import (
    MongoUserViewRepository,
)

from .cache_di import cache
from .shared_di import mongo_client

_cached_user_view_repository = CachedUserViewRepository(
    MongoUserViewRepository(mongo_client),
    cache,
    ttl_seconds=CACHE_TTL_SECONDS,
)
user_view_repository: UserViewRepository = _cached_user_view_repository

user_view_cache_invalidator = InvalidateUserViewsCache(_cached_user_view_repository)


def user_views_query_handlers() -> Dict[Type[Query], Callable[[Query], Any]]:
    user_searcher = UserSearcher(user_view_repository)
    user_finder_by_id = UserFinderById(user_view_repository)

    return {
        SearchUsersQuery:  SearchUsersQueryHandler(user_searcher),
        FindUserByIdQuery: FindUserByIdQueryHandler(user_finder_by_id),
    }
