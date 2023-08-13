from sqlalchemy.orm import Session

from app.auth import crud, models
from app.core.config import settings
from app.db.init_db import init_db


class TestDb:
    def test_db_init_creates_superuser(self, db: Session) -> None:
        init_db(db)
        user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        assert user is not None
        assert isinstance(user, models.User)
        assert user.email == settings.FIRST_SUPERUSER_EMAIL
