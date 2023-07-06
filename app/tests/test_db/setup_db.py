from app.auth.models import User
from app.auth.security import get_password_hash
from app.core.config import settings
from app.tests.test_db.session import TestingSessionLocal


def init_db() -> None:
    session = TestingSessionLocal()
    super_user = User(
        email=settings.TEST_SUPERUSER_EMAIL,
        hashed_password=get_password_hash(settings.TEST_SUPERUSER_PASSWORD),
        is_activated=True,
        is_superuser=True,
    )
    user = User(
        email=settings.TEST_USER_EMAIL,
        hashed_password=get_password_hash(settings.TEST_USER_PASSWORD),
        is_activated=True,
    )
    session.add_all([super_user, user])
    session.commit()
