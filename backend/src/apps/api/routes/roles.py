from fastapi import APIRouter

from apps.api.dependencies import get_query_bus
from modules.role_views.application.list_roles.list_roles_query import ListRolesQuery

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=dict)
def list_roles():
    roles = get_query_bus().ask(ListRolesQuery())
    return {"items": [r.to_primitive() for r in roles]}
