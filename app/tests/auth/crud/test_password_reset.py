from datetime import datetime
from typing import Generator

import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.auth import crud, models, schemas
from app.core.config import settings


class TestPasswordReset:
    user_id: int = 1
    second_user_id: int = 2
    value: str

    @pytest.fixture(name="reset_token")
    def create_reset_token(self, db: Session) -> models.PasswordResetToken:
        token_in = schemas.PasswordResetTokenCreate(user_id=self.user_id)
        token = crud.password_reset_token.generate(db, obj_in=token_in)
        self.value = token.value
        return token

    @pytest.fixture(name="multiple_reset_tokens")
    def create_multiple_reset_tokens(self, db: Session) -> list[models.PasswordResetToken]:
        token_in = schemas.PasswordResetTokenCreate(user_id=self.user_id)
        tokens = [crud.password_reset_token.generate(db, obj_in=token_in) for _ in range(5)]
        return tokens

    @pytest.fixture(name="reset_tokens_for_different_users")
    def create_reset_tokens_for_different_users(self, db: Session) -> dict[int, models.PasswordResetToken]:
        tokens = {
            user_id: crud.password_reset_token.generate(db, obj_in=schemas.PasswordResetTokenCreate(user_id=user_id))
            for user_id in (self.user_id, self.second_user_id)
        }
        return tokens

    @pytest.fixture(name="override_token_expire_time")
    def override_token_expiration_time(self) -> Generator:
        old_setting = settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 0
        yield
        settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = old_setting

    def test_generate_token(self, reset_token: models.PasswordResetToken) -> None:
        assert isinstance(reset_token, models.PasswordResetToken)
        assert reset_token.user_id == self.user_id
        assert isinstance(reset_token.expires_at, datetime)

    def test_generate_token_is_invalidated_should_be_false_by_default(
        self, reset_token: models.PasswordResetToken
    ) -> None:
        assert not crud.password_reset_token.is_invalidated(reset_token)

    def test_invalidate_token(self, db: Session, reset_token: models.PasswordResetToken) -> None:
        crud.password_reset_token.invalidate(db, token=reset_token)
        assert crud.password_reset_token.is_invalidated(token=reset_token)

    def test_invalidate_all_tokens(self, db: Session, multiple_reset_tokens: list[models.PasswordResetToken]) -> None:
        crud.password_reset_token.invalidate_all(db, user_id=self.user_id)
        for token in multiple_reset_tokens:
            assert crud.password_reset_token.is_invalidated(token=token)

    def test_get_token_by_value(self, db: Session, reset_token: models.PasswordResetToken) -> None:
        token = crud.password_reset_token.get_by_value(db, value=self.value)
        assert isinstance(token, models.PasswordResetToken)
        assert jsonable_encoder(token) == jsonable_encoder(reset_token)

    def test_is_expired_if_not_expired(self, reset_token: models.PasswordResetToken) -> None:
        assert not crud.password_reset_token.is_expired(reset_token)

    def test_is_expired_if_expired(
        self, override_token_expire_time: None, reset_token: models.PasswordResetToken  # pylint: disable=W0613
    ) -> None:
        assert crud.password_reset_token.is_expired(reset_token)

    def test_invalidate_all_tokens_for_one_user_should_not_invalidate_for_other_users(
        self, db: Session, reset_tokens_for_different_users: dict[int, models.PasswordResetToken]
    ) -> None:
        crud.password_reset_token.invalidate_all(db, user_id=self.user_id)
        assert crud.password_reset_token.is_invalidated(reset_tokens_for_different_users[self.user_id])
        assert not crud.password_reset_token.is_invalidated(reset_tokens_for_different_users[self.second_user_id])
