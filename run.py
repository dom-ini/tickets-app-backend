import uvicorn

from app.db.init_db import init_db
from app.db.session import SessionLocal


def init() -> None:
    db = SessionLocal()
    init_db(db)


if __name__ == "__main__":
    init()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
