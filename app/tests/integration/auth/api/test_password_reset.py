import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from app.auth import crud
from app.auth.models import PasswordResetToken, User
from app.auth.schemas import PasswordResetTokenCreate
from app.auth.utils import generate_valid_password
from app.common.deps import Mailer
from app.core.config import settings


class TestPasswordReset:
    @pytest.fixture()
    def mock_add_task(self, mocker: MockerFixture) -> MagicMock:
        return mocker.patch("fastapi.BackgroundTasks.add_task")

    @pytest.fixture()
    def password_reset_token(self, db: Session, test_user: User) -> PasswordResetToken:
        token_in = PasswordResetTokenCreate(user_id=test_user.id)
        token = crud.password_reset_token.create(db, obj_in=token_in)
        return token

    @pytest.fixture()
    def invalidated_token(self, db: Session, password_reset_token: PasswordResetToken) -> PasswordResetToken:
        token = crud.password_reset_token.invalidate(db, token=password_reset_token)
        return token

    @pytest.fixture()
    def expired_token(self, db: Session, password_reset_token: PasswordResetToken) -> PasswordResetToken:
        password_reset_token.expires_at = datetime.datetime(2010, 1, 1)
        db.commit()
        db.refresh(password_reset_token)
        return password_reset_token

    def test_request_password_reset_user_exists(self, client: TestClient, mail_engine: Mailer) -> None:
        payload = {"email": settings.TEST_USER_EMAIL}
        with mail_engine.record_messages() as outbox:
            r = client.post(f"{settings.API_V1_STR}/auth/password/reset", json=payload)
            result = r.json()
            assert r.status_code == status.HTTP_200_OK
            assert "message" in result
            assert len(outbox) == 1

    def test_request_password_reset_user_does_not_exist(self, client: TestClient, mock_add_task: MagicMock) -> None:
        payload = {"email": "invalid_email@example.com"}
        r = client.post(f"{settings.API_V1_STR}/auth/password/reset", json=payload)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert "message" in result
        mock_add_task.assert_not_called()

    def test_reset_password(
        self, client: TestClient, password_reset_token: PasswordResetToken, test_user: User
    ) -> None:
        old_password_hash = test_user.hashed_password
        payload = {"token": password_reset_token.value, "new_password": generate_valid_password()}
        r = client.post(f"{settings.API_V1_STR}/auth/password/reset/confirm", json=payload)
        assert r.status_code == status.HTTP_200_OK
        assert test_user.hashed_password != old_password_hash

    def test_reset_password_invalid_token(self, client: TestClient) -> None:
        payload = {"token": "invalid", "new_password": generate_valid_password()}
        r = client.post(f"{settings.API_V1_STR}/auth/password/reset/confirm", json=payload)
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_reset_password_invalidated_token(self, client: TestClient, invalidated_token: PasswordResetToken) -> None:
        payload = {"token": invalidated_token.value, "new_password": generate_valid_password()}
        r = client.post(f"{settings.API_V1_STR}/auth/password/reset/confirm", json=payload)
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_reset_password_expired_token(self, client: TestClient, expired_token: PasswordResetToken) -> None:
        payload = {"token": expired_token.value, "new_password": generate_valid_password()}
        r = client.post(f"{settings.API_V1_STR}/auth/password/reset/confirm", json=payload)
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_reset_password_weak_password(self, client: TestClient, password_reset_token: PasswordResetToken) -> None:
        payload = {"token": password_reset_token.value, "new_password": "weak"}
        r = client.post(f"{settings.API_V1_STR}/auth/password/reset/confirm", json=payload)
        assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
