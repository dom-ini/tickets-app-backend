from contextlib import contextmanager
from typing import Generator
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.auth import crud
from app.auth.deps import (
    create_verification_token,
    open_registration_allowed,
    register_new_user_and_send_verification_email,
    register_user,
    user_create_unique_email,
    user_update_unique_email,
    validate_unique_email,
    verify_account,
)
from app.auth.exceptions import EmailAlreadyTaken, InvalidToken, OpenRegistrationNotAllowed
from app.auth.schemas import UserCreate, UserCreateOpen, UserUpdate
from app.auth.utils import generate_valid_password
from app.core.config import settings


@pytest.fixture(name="mock_crud_user")
def get_mock_crud_user(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch.object(crud, "user")
    return mocked


@pytest.fixture(name="mock_crud_token")
def get_mock_crud_verification_token(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch.object(crud, "verification_token")
    return mocked


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


def test_register_user_creates_user(mock_db: Mock, mock_crud_user: Mock) -> None:
    form = UserCreate(email="email@example.com", password=generate_valid_password())
    register_user(mock_db, registration_form=form)

    mock_crud_user.create.assert_called_once()


def test_create_verification_token(mock_db: Mock, mock_crud_token: Mock) -> None:
    user = Mock()
    user.id = 1
    create_verification_token(mock_db, user=user)

    mock_crud_token.create.assert_called_once()


def test_register_new_user_and_send_verification_email_returns_user(mocker: MockerFixture) -> None:
    user_mock = Mock()
    mock = Mock()
    mocker.patch("app.auth.deps.send_new_user_email")
    result = register_new_user_and_send_verification_email(
        user=user_mock, token=mock, background_tasks=mock, mailer=mock
    )

    assert result == user_mock


def test_register_new_user_and_send_verification_email_sends_email(mocker: MockerFixture) -> None:
    mock_background_tasks = Mock()
    mock_mailer = Mock()
    mock = Mock()
    mock_send_email = mocker.patch("app.auth.deps.send_new_user_email")
    register_new_user_and_send_verification_email(
        user=mock, token=mock, background_tasks=mock_background_tasks, mailer=mock_mailer
    )

    mock_background_tasks.add_task.assert_called_once_with(mock_mailer.send, mock_send_email())


def verify_account_if_token_does_not_exist_should_raise_error(mock_db: Mock) -> None:
    token = "invalid"

    with pytest.raises(InvalidToken):
        verify_account(mock_db, token=token)


def verify_account_should_activate_user(mock_db: Mock, mock_crud_token: Mock, mock_crud_user: Mock) -> None:
    mock_crud_token.get_by_value.return_value = Mock()
    verify_account(mock_db, "token")

    mock_crud_user.activate.assert_called_once()


def verify_account_should_remove_verification_token(
    mock_db: Mock, mock_crud_token: Mock, mock_crud_user: Mock  # pylint: disable=W0613
) -> None:
    mock_crud_token.get_by_value.return_value = Mock()
    verify_account(mock_db, "token")

    mock_crud_token.remove.assert_called_once()
