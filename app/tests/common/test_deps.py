import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.security import create_access_token
from app.common.deps import get_current_user, get_db


class TestDeps:
    def test_get_db(self) -> None:
        db = next(get_db())
        assert db is not None
        assert isinstance(db, Session)

    def test_get_current_user_with_incorrect_token_should_fail(self, db: Session) -> None:
        with pytest.raises(HTTPException):
            get_current_user(db, token="incorrect.token")

    def test_get_current_user_incorrect_user_should_fail(self, db: Session) -> None:
        token = create_access_token(subject=9999)
        with pytest.raises(HTTPException):
            get_current_user(db, token=token)
