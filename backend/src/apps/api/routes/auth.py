from fastapi import APIRouter, Request, status
from pydantic import BaseModel, EmailStr, Field

from apps.api.dependencies import get_command_bus
from apps.api.rate_limit import limiter
from modules.auth.application.login.login_command import LoginCommand
from modules.auth.application.refresh.refresh_token_command import RefreshTokenCommand
from modules.auth.application.register.register_command import RegisterCommand
from apps.api.config import LOGIN_RATE_LIMIT

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(body: RegisterRequest, request: Request):
    return get_command_bus().dispatch(RegisterCommand(
        name=body.name,
        email=body.email,
        password=body.password,
        ip_address=_client_ip(request),
    ))


@router.post("/login")
@limiter.limit(LOGIN_RATE_LIMIT)
def login(body: LoginRequest, request: Request):
    return get_command_bus().dispatch(LoginCommand(
        email=body.email,
        password=body.password,
        ip_address=_client_ip(request),
    ))


@router.post("/refresh")
@limiter.limit("30/minute")
def refresh(body: RefreshRequest, request: Request):
    return get_command_bus().dispatch(RefreshTokenCommand(
        refresh_token=body.refresh_token,
        ip_address=_client_ip(request),
    ))



# ── Helpers ───────────────────────────────────────────────────────────────────
def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""
