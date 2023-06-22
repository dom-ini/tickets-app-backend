from typing import Any

from fastapi import FastAPI

from app.core.config import settings
from app.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(api_router)


@app.get("/")
async def root() -> Any:
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str) -> Any:
    return {"message": f"Hello {name}"}
