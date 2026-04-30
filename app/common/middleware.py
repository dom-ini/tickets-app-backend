from typing import Awaitable, Callable, Iterable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

EXCLUDED_ROUTES: Iterable[str] = ("/api/v1/auth/login",)


class DemoModeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, enabled: bool = False, excluded_routes: Iterable[str] = EXCLUDED_ROUTES) -> None:
        super().__init__(app)
        self.enabled = enabled
        self.blocked_methods: set[str] = {"POST", "PATCH", "PUT", "DELETE"}

        self.excluded_routes = set(excluded_routes)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if self.enabled and request.method in self.blocked_methods and request.url.path not in self.excluded_routes:
            return JSONResponse(
                {
                    "detail": "Demo mode: request accepted but not persisted.",
                    "method": request.method,
                    "path": request.url.path,
                },
                status_code=200,
            )

        response = await call_next(request)
        return response
