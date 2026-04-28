from typing import Callable

from fastapi import HTTPException, Request, status


def require_roles(*roles: str) -> Callable:
    allowed = frozenset(roles)

    def dependency(request: Request):
        auth = getattr(request.state, "auth", None)
        if auth is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "NotAuthenticated", "message": "Not authenticated"},
            )
        if auth.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "RoleNotAllowed",
                    "message": f"Role <{auth.role}> is not allowed",
                    "details": {"required": sorted(allowed)},
                },
            )
        return auth

    return dependency
