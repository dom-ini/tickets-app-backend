from dataclasses import dataclass
from typing import Any, Type

from app.auth.models import User
from app.auth.security import get_password_hash
from app.core.config import settings
from app.db.base_class import Base


@dataclass
class InitialDataEntry:
    model: Type[Base]
    data: list[dict[str, Any]]


INITIAL_DATA = {
    "users": InitialDataEntry(
        model=User,
        data=[
            {
                "email": settings.TEST_SUPERUSER_EMAIL,
                "hashed_password": get_password_hash(settings.TEST_SUPERUSER_PASSWORD),
                "is_activated": True,
                "is_superuser": True,
            },
            {
                "email": settings.TEST_USER_EMAIL,
                "hashed_password": get_password_hash(settings.TEST_USER_PASSWORD),
                "is_activated": True,
            },
        ],
    )
}
