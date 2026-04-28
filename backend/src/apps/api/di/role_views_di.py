from typing import Any, Callable, Dict, Type

from apps.api.config import CACHE_TTL_SECONDS
from modules.role_views.application.list_roles.list_roles_query import ListRolesQuery
from modules.role_views.application.list_roles.list_roles_query_handler import ListRolesQueryHandler
from modules.role_views.application.list_roles.role_lister import RoleLister
from modules.role_views.domain.role_view_repository import RoleViewRepository
from modules.role_views.infrastructure.persistence.cached_role_view_repository import (
    CachedRoleViewRepository,
)
from modules.role_views.infrastructure.persistence.mongo_role_view_repository import (
    MongoRoleViewRepository,
)
from modules.shared.domain.query import Query

from .cache_di import cache
from .shared_di import mongo_client


role_view_repository: RoleViewRepository = CachedRoleViewRepository(
    MongoRoleViewRepository(mongo_client),
    cache,
    ttl_seconds=CACHE_TTL_SECONDS,
)


def role_views_query_handlers() -> Dict[Type[Query], Callable[[Query], Any]]:
    lister = RoleLister(role_view_repository)

    return {
        ListRolesQuery: ListRolesQueryHandler(lister),
    }
