from fastapi import APIRouter, Request, status
from fastapi.responses import Response

from apps.api.dependencies import get_command_bus, get_query_bus
from modules.auth.application.logout.logout_command import LogoutCommand
from modules.user_views.application.find_by_id.find_user_by_id_query import (
    FindUserByIdQuery,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request):
    get_command_bus().dispatch(LogoutCommand(session_id=request.state.auth.session_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me")
def me(request: Request):
    auth = request.state.auth
    user = get_query_bus().ask(FindUserByIdQuery(id=auth.user_id))
    if user is None:
        return {"id": auth.user_id, "role": {"id": auth.role_id, "role": auth.role}}
    return user.to_primitive()
