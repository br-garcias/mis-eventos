from __future__ import annotations

import json
import logging
import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log = logging.getLogger("api.access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - started) * 1000
            _emit(request, 500, elapsed_ms)
            raise

        elapsed_ms = (time.perf_counter() - started) * 1000
        _emit(request, response.status_code, elapsed_ms)
        return response


def _emit(request: Request, status_code: int, elapsed_ms: float) -> None:
    auth = getattr(request.state, "auth", None)
    payload: dict[str, Any] = {
        "request_id": getattr(request.state, "request_id", None),
        "user_id": getattr(auth, "user_id", None) if auth else None,
        "method": request.method,
        "path": request.url.path,
        "status_code": status_code,
        "duration_ms": round(elapsed_ms, 2),
    }
    log.info(json.dumps(payload))
