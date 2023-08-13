from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from starlette import status

from app.common.deps import Mailer
from app.core.config import settings


class TestPasswordReset:
    @pytest.fixture()
    def mock_add_task(self, mocker: MockerFixture) -> MagicMock:
        return mocker.patch("fastapi.BackgroundTasks.add_task")

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
