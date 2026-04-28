from fastapi import HTTPException, Request, status

from apps.api.dependencies import get_query_bus
from modules.auth.application.validate.validate_token_query import ValidateTokenQuery


def authenticate(request: Request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "NotAuthenticated", "message": "Missing Authorization header"},
        )
    token = header[len("Bearer "):]
    try:
        auth = get_query_bus().ask(ValidateTokenQuery(token=token))
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "InvalidToken", "message": str(e)},
        )
    if auth is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "NotAuthenticated", "message": "Invalid token"},
        )
    request.state.auth = auth
    return auth
