from datetime import datetime
from typing import Any, ParamSpec, Protocol, Type, TypeVar

import pytest

from app.auth.models import PasswordResetToken, User, VerificationToken
from app.tests.unit.utils import create_user_instance

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class ModelWithUser(Protocol[P, R_co]):
    user: User

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co:
        ...


def test_str_user() -> None:
    email = "some-mail@example.com"
    user = create_user_instance(email)
    assert email in str(user)


@pytest.mark.parametrize(
    "model,additional_payload", [(PasswordResetToken, {"expires_at": datetime.utcnow()}), (VerificationToken, {})]
)
def test_str_tokens(model: Type[ModelWithUser], additional_payload: dict[str, Any], user_instance: User) -> None:
    payload = {"value": "token-value", "user_id": 1, **additional_payload}
    token = model(**payload)
    token.user = user_instance
    assert str(user_instance) in str(token)
