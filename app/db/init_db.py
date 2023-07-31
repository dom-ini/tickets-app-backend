from sqlalchemy.orm import Session

from app.auth import crud
from app.auth.schemas import UserCreate
from app.core.config import settings


def init_db(db: Session) -> None:
    superuser = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not superuser:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_activated=True,
        )
        crud.user.create(db, obj_in=user_in)
