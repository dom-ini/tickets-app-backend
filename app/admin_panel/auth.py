import dataclasses
from typing import Any, Literal, Optional

import httpx
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend

from app.core.config import settings

TOKEN_SESSION_KEY = "token"


@dataclasses.dataclass
class RequestUser:
    id: int
    email: str
    is_superuser: bool


async def _make_request(
    url: str, method: Literal["get", "post"], **request_kwargs: dict[str, Any]
) -> dict[str, Any] | None:
    async with httpx.AsyncClient() as client:
        try:
            r = await getattr(client, method)(
                f"{settings.SERVER_PROTOCOL}://{settings.SERVER_HOST}{settings.API_V1_STR}{url}", **request_kwargs
            )
            r.raise_for_status()
            return r.json()
        except (httpx.RequestError, httpx.HTTPError):
            return None


async def get_access_token(payload: dict[str, Any]) -> str | None:
    result = await _make_request("/auth/login", method="post", data=payload)
    token = result.get("access_token") if result is not None else result
    return token


async def get_user(token: str) -> RequestUser | None:
    result = await _make_request("/auth/test-token", method="get", headers={"Authorization": f"Bearer {token}"})
    if result is None:
        return result
    user = RequestUser(id=result["id"], email=result["email"], is_superuser=result["is_superuser"])
    return user


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        payload = {"username": username, "password": password}
        token = await get_access_token(payload)

        if not token:
            return False

        request.session.update({TOKEN_SESSION_KEY: token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        token = request.session.get(TOKEN_SESSION_KEY)
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=status.HTTP_307_TEMPORARY_REDIRECT)

        user = await get_user(token)
        request.state.user = user
        if not user or not user.is_superuser:
            return RedirectResponse(request.url_for("admin:login"), status_code=status.HTTP_307_TEMPORARY_REDIRECT)

        return None


authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
