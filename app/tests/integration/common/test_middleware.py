import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.common.middleware import DemoModeMiddleware


@pytest.fixture(name="app")
def get_app() -> FastAPI:
    app = FastAPI()

    async def dummy_endpoint() -> JSONResponse:
        return JSONResponse({"test": "test"})

    app.add_api_route("/test", dummy_endpoint, methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
    return app


@pytest.mark.parametrize("is_enabled", [True, False])
@pytest.mark.parametrize("method", ["GET", "POST", "PATCH", "PUT", "DELETE"])
def test_demo_mode_middleware(app: FastAPI, is_enabled: bool, method: str) -> None:
    app.add_middleware(DemoModeMiddleware, enabled=is_enabled)

    with TestClient(app) as client:
        response = client.request(method, "/test")

    should_block = is_enabled and method in {"POST", "PATCH", "PUT", "DELETE"}
    was_blocked = response.json().get("blocked", False)
    assert was_blocked == should_block


def test_demo_mode_middleware_should_not_block_excluded_route(app: FastAPI) -> None:
    app.add_middleware(DemoModeMiddleware, enabled=True, excluded_routes=("/test",))

    with TestClient(app) as client:
        response = client.post("/test")

    assert not response.json().get("blocked", False)
