import uuid

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from apps.api.dependencies import get_command_bus, get_query_bus
from modules.user_views.application.find_by_id.find_user_by_id_query import FindUserByIdQuery
from modules.user_views.application.search.search_users_query import SearchUsersQuery
from modules.event_views.domain.event_view_dto import Page
from modules.user_views.domain.user_view_dto import UserDetailView
from modules.users.application.create.create_user_command import CreateUserCommand
from modules.users.application.toggle.toggle_user_command import ToggleUserCommand
from modules.users.application.update.update_user_command import UpdateUserCommand

router = APIRouter(prefix="/users", tags=["users"])


# ── Request models ────────────────────────────────────────────────────────────
class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_name: str


class UpdateUserRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role_id: str | None = None


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("", status_code=status.HTTP_201_CREATED)
def create(body: CreateUserRequest):
    user_id = str(uuid.uuid4())
    get_command_bus().dispatch(CreateUserCommand(
        id=user_id,
        name=body.name,
        email=body.email,
        password=body.password,
        role_name=body.role_name,
    ))
    return {"id": user_id}


@router.patch("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def update(user_id: str, body: UpdateUserRequest):
    get_command_bus().dispatch(UpdateUserCommand(
        id=user_id,
        name=body.name,
        email=body.email,
        password=body.password,
        role_id=body.role_id,
    ))


@router.post("/{user_id}/toggle", status_code=status.HTTP_204_NO_CONTENT)
def toggle(user_id: str):
    get_command_bus().dispatch(ToggleUserCommand(id=user_id))


# ── Read side (user_views) ────────────────────────────────────────────────────
@router.get("", response_model=Page)
def search(
    email: str | None = None,
    name: str | None = None,
    role_id: str | None = None,
    page: int = 1,
    size: int = 20,
) -> Page:
    return get_query_bus().ask(SearchUsersQuery(
        email=email,
        name=name,
        role_id=role_id,
        page=page,
        size=size,
    ))


@router.get("/{user_id}")
def detail(user_id: str) -> UserDetailView:
    result = get_query_bus().ask(FindUserByIdQuery(id=user_id))
    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"code": "UserNotFoundError", "message": f"User <{user_id}> not found"},
        )
    return result
