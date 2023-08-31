from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.auth.security import create_access_token, get_password_hash, pwd_context, verify_password
from app.core.config import settings


@pytest.fixture(name="mock_verify_password")
def get_mock_verify_password(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch.object(pwd_context, "verify")
    return mocked


@pytest.fixture(name="mock_jwt_encode")
def get_mock_jwt_encode(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch("app.auth.security.jwt.encode")
    return mocked


@pytest.fixture(name="override_token_settings")
def do_override_token_settings() -> Generator:
    secret, algorithm = settings.SECRET_KEY, settings.JWT_ALGORITHM
    settings.SECRET_KEY = "dummy-secret"
    settings.JWT_ALGORITHM = "dummy-algorithm"
    yield
    settings.SECRET_KEY = secret
    settings.JWT_ALGORITHM = algorithm


def test_get_password_hash_returns_string() -> None:
    hashed = get_password_hash("Test1234!")
    assert isinstance(hashed, str)


def test_get_password_hash_does_not_return_original_password() -> None:
    password = "Test1234!"
    hashed = get_password_hash(password)
    assert hashed != password


@pytest.mark.parametrize("verified", [True, False])
def test_verify_password(mock_verify_password: Mock, verified: bool) -> None:
    mock_verify_password.return_value = verified
    assert verify_password("pass", "pass") == verified


def test_create_access_token_returns_token(mock_jwt_encode: Mock) -> None:
    expected_token = "expected"
    mock_jwt_encode.return_value = expected_token
    token = create_access_token("")

    assert token == expected_token


def test_create_access_token_correct_payload(
    mock_jwt_encode: Mock, override_token_settings: Generator, mocker: MockerFixture  # pylint: disable=W0613
) -> None:
    subject = "subject"
    now = datetime.utcnow()
    mock_date = mocker.patch("app.auth.security.datetime")
    mock_date.utcnow.return_value = now

    create_access_token(subject)
    payload = {"exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "sub": subject}

    mock_jwt_encode.assert_called_once_with(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
