from datetime import datetime
from typing import Any, Type

import pytest

from app.auth.models import PasswordResetToken, User, VerificationToken
from app.db.base_class import Base
from app.tests.unit.utils import create_user_instance


def test_str_user() -> None:
    email = "some-mail@example.com"
    user = create_user_instance(email)
    assert email in str(user)


@pytest.mark.parametrize(
    "model,additional_payload", [(PasswordResetToken, {"expires_at": datetime.utcnow()}), (VerificationToken, {})]
)
def test_str_tokens(model: Type[Base], additional_payload: dict[str, Any], user_instance: User) -> None:
    payload = {"value": "token-value", "user_id": 1, **additional_payload}
    token = model(**payload)
    token.user = user_instance
    assert str(user_instance) in str(token)
