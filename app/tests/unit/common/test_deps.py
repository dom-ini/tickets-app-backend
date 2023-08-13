from sqlalchemy.orm import Session

from app.common.deps import get_db


class TestDeps:
    def test_get_db(self) -> None:
        db = next(get_db())
        assert db is not None
        assert isinstance(db, Session)
