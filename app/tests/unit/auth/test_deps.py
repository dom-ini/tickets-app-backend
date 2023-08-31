from contextlib import contextmanager
from typing import Generator
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.auth import crud
from app.auth.deps import (
    open_registration_allowed,
    user_create_unique_email,
    user_update_unique_email,
    validate_unique_email,
)
from app.auth.exceptions import EmailAlreadyTaken, OpenRegistrationNotAllowed
from app.auth.schemas import UserCreateOpen, UserUpdate
from app.auth.utils import generate_valid_password
from app.core.config import settings


@pytest.fixture(name="mock_current_user")
def get_mock_current_user() -> Mock:
    return Mock()


@pytest.fixture(name="mock_validate_email")
def get_mock_validate_unique_email(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch("app.auth.deps.validate_unique_email")
    return mocked


@contextmanager
def change_open_registration(new_value: bool) -> Generator:
    old_setting = settings.USERS_OPEN_REGISTRATION
    settings.USERS_OPEN_REGISTRATION = new_value
    yield
    settings.USERS_OPEN_REGISTRATION = old_setting


@pytest.fixture(name="disallow_open_registration")
def get_disallow_open_registration() -> Generator:
    with change_open_registration(False):
        yield


@pytest.fixture(name="allow_open_registration")
def get_allow_open_registration() -> Generator:
    with change_open_registration(True):
        yield


def test_validate_unique_email(mock_db: Mock, mocker: MockerFixture) -> None:
    mocker.patch.object(crud.user, "get_by_email", return_value=None)
    try:
        validate_unique_email(mock_db, email="email")
    except EmailAlreadyTaken as exc:
        pytest.fail(f"An exception was raised: {exc}")


def test_validate_unique_email_existing_email_should_fail(mock_db: Mock, mocker: MockerFixture) -> None:
    mocker.patch.object(crud.user, "get_by_email", return_value=Mock())
    with pytest.raises(EmailAlreadyTaken):
        validate_unique_email(mock_db, email="email")


def test_user_update_unique_email_no_email_given(
    mock_db: Mock, mock_current_user: Mock, mock_validate_email: Mock
) -> None:
    obj_in = UserUpdate()
    user_update_unique_email(mock_db, current_user=mock_current_user, user_in=obj_in)

    mock_validate_email.assert_not_called()


def test_user_update_unique_email_current_user_email_given(
    mock_db: Mock, mock_current_user: Mock, mock_validate_email: Mock
) -> None:
    email = "email@example.com"
    mock_current_user.email = email
    obj_in = UserUpdate(email=email)
    user_update_unique_email(mock_db, current_user=mock_current_user, user_in=obj_in)

    mock_validate_email.assert_not_called()


def test_user_update_unique_email_unique_email_given(
    mock_db: Mock, mock_current_user: Mock, mock_validate_email: Mock
) -> None:
    email = "email@example.com"
    mock_current_user.email = "different@example.com"
    obj_in = UserUpdate(email=email)
    result = user_update_unique_email(mock_db, current_user=mock_current_user, user_in=obj_in)

    mock_validate_email.assert_called_once()
    assert result == obj_in


def test_user_update_unique_email_existing_email_given(
    mock_db: Mock, mock_current_user: Mock, mock_validate_email: Mock
) -> None:
    email = "email@example.com"
    mock_current_user.email = "different@example.com"
    obj_in = UserUpdate(email=email)
    mock_validate_email.side_effect = EmailAlreadyTaken

    with pytest.raises(EmailAlreadyTaken):
        user_update_unique_email(mock_db, current_user=mock_current_user, user_in=obj_in)


def test_user_create_unique_email_unique_email_given(
    mock_db: Mock, mock_validate_email: Mock  # pylint: disable=W0613
) -> None:
    email = "email@example.com"
    obj_in = UserCreateOpen(email=email, password=generate_valid_password())
    result = user_create_unique_email(mock_db, user_in=obj_in)

    assert result == obj_in


def test_user_create_unique_email_existing_email_given(mock_db: Mock, mock_validate_email: Mock) -> None:
    email = "email@example.com"
    obj_in = UserCreateOpen(email=email, password=generate_valid_password())
    mock_validate_email.side_effect = EmailAlreadyTaken

    with pytest.raises(EmailAlreadyTaken):
        user_create_unique_email(mock_db, user_in=obj_in)


def test_open_registration_allowed_when_allowed(allow_open_registration: Generator) -> None:  # pylint: disable=W0613
    try:
        open_registration_allowed()
    except OpenRegistrationNotAllowed as exc:
        pytest.fail(f"An exception was raised: {exc}")


def test_open_registration_allowed_when_disallowed(
    disallow_open_registration: Generator,  # pylint: disable=W0613
) -> None:
    with pytest.raises(OpenRegistrationNotAllowed):
        open_registration_allowed()
