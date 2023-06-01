from typing import Any

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root() -> Any:
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str) -> Any:
    return {"message": f"Hello {name}"}
