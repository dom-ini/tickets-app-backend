# pylint: disable=R0913
from contextlib import contextmanager
from typing import Generator, Type
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.auth import crud
from app.auth.deps import (
    authenticate_and_authorize_user,
    create_verification_token,
    invalidate_password_reset_token,
    open_registration_allowed,
    process_reset_password_request,
    register_new_user_and_send_verification_email,
    register_user,
    reset_user_password,
    user_create_unique_email,
    user_exists,
    user_update_unique_email,
    validate_unique_email,
    verify_account,
)
from app.auth.exceptions import (
    EmailAlreadyTaken,
    InvalidCredentials,
    InvalidToken,
    OpenRegistrationNotAllowed,
    UserDisabled,
    UserNotActivated,
)
from app.auth.schemas import UserCreate, UserCreateOpen, UserUpdateWithCurrentPassword
from app.auth.utils import generate_valid_password
from app.core.config import settings


@pytest.fixture(name="mock_crud_user")
def get_mock_crud_user(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch.object(crud, "user")
    return mocked


@pytest.fixture(name="mock_crud_verification_token")
def get_mock_crud_verification_token(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch.object(crud, "verification_token")
    return mocked


@pytest.fixture(name="mock_crud_password_reset")
def get_mock_crud_password_reset(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch.object(crud, "password_reset_token")
    return mocked


@pytest.fixture(name="mock_current_user")
def get_mock_current_user() -> Mock:
    return Mock(id=1)


@pytest.fixture(name="mock_background_tasks")
def get_mock_background_tasks() -> Mock:
    return Mock()


@pytest.fixture(name="mock_mailer")
def get_mock_mailer() -> Mock:
    return Mock()


@pytest.fixture(name="mock_validate_email")
def get_mock_validate_unique_email(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch("app.auth.deps.validate_unique_email")
    return mocked


@pytest.fixture(name="mock_send_password_reset_request_mail")
def get_mock_send_password_reset_request_mail(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch("app.auth.deps.send_password_reset_request_mail")
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
    obj_in = UserUpdateWithCurrentPassword(current_password="password")
    user_update_unique_email(mock_db, current_user=mock_current_user, user_in=obj_in)

    mock_validate_email.assert_not_called()


def test_user_update_unique_email_current_user_email_given(
    mock_db: Mock, mock_current_user: Mock, mock_validate_email: Mock
) -> None:
    email = "email@example.com"
    mock_current_user.email = email
    obj_in = UserUpdateWithCurrentPassword(email=email, current_password="password")
    user_update_unique_email(mock_db, current_user=mock_current_user, user_in=obj_in)

    mock_validate_email.assert_not_called()


def test_user_update_unique_email_unique_email_given(
    mock_db: Mock, mock_current_user: Mock, mock_validate_email: Mock
) -> None:
    email = "email@example.com"
    mock_current_user.email = "different@example.com"
    obj_in = UserUpdateWithCurrentPassword(email=email, current_password="password")
    result = user_update_unique_email(mock_db, current_user=mock_current_user, user_in=obj_in)

    mock_validate_email.assert_called_once()
    assert result == obj_in


def test_user_update_unique_email_existing_email_given(
    mock_db: Mock, mock_current_user: Mock, mock_validate_email: Mock
) -> None:
    email = "email@example.com"
    mock_current_user.email = "different@example.com"
    obj_in = UserUpdateWithCurrentPassword(email=email, current_password="password")
    mock_validate_email.side_effect = EmailAlreadyTaken

    with pytest.raises(EmailAlreadyTaken):
        user_update_unique_email(mock_db, current_user=mock_current_user, user_in=obj_in)


@pytest.mark.usefixtures("mock_validate_email")
def test_user_create_unique_email_unique_email_given(mock_db: Mock) -> None:
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


@pytest.mark.usefixtures("allow_open_registration")
def test_open_registration_allowed_when_allowed() -> None:
    try:
        open_registration_allowed()
    except OpenRegistrationNotAllowed as exc:
        pytest.fail(f"An exception was raised: {exc}")


@pytest.mark.usefixtures("disallow_open_registration")
def test_open_registration_allowed_when_disallowed() -> None:
    with pytest.raises(OpenRegistrationNotAllowed):
        open_registration_allowed()


def test_register_user_creates_user(mock_db: Mock, mock_crud_user: Mock) -> None:
    form = UserCreate(email="email@example.com", password=generate_valid_password())
    register_user(mock_db, registration_form=form)

    mock_crud_user.create.assert_called_once()


def test_create_verification_token(mock_db: Mock, mock_crud_verification_token: Mock) -> None:
    user = Mock()
    user.id = 1
    create_verification_token(mock_db, user=user)

    mock_crud_verification_token.create.assert_called_once()


def test_register_new_user_and_send_verification_email_returns_user(mocker: MockerFixture) -> None:
    user_mock = Mock()
    mock = Mock()
    mocker.patch("app.auth.deps.send_new_user_email")
    result = register_new_user_and_send_verification_email(
        user=user_mock, token=mock, background_tasks=mock, mailer=mock
    )

    assert result == user_mock


def test_register_new_user_and_send_verification_email_sends_email(
    mock_background_tasks: Mock, mock_mailer: Mock, mocker: MockerFixture
) -> None:
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


def verify_account_should_activate_user(
    mock_db: Mock, mock_crud_verification_token: Mock, mock_crud_user: Mock
) -> None:
    mock_crud_verification_token.get_by_value.return_value = Mock()
    verify_account(mock_db, "token")

    mock_crud_user.activate.assert_called_once()


@pytest.mark.usefixtures("mock_crud_user")
def verify_account_should_remove_verification_token(mock_db: Mock, mock_crud_verification_token: Mock) -> None:
    mock_crud_verification_token.get_by_value.return_value = Mock()
    verify_account(mock_db, "token")

    mock_crud_verification_token.remove.assert_called_once()


@pytest.mark.parametrize(
    "user,exc",
    [
        (None, InvalidCredentials),
        (Mock(is_activated=False), UserNotActivated),
        (Mock(is_activated=True, is_disabled=True), UserDisabled),
        (Mock(is_activated=True, is_disabled=False), None),
    ],
)
def test_authenticate_and_authorize_user(
    mock_db: Mock, user: Mock | None, exc: Type[Exception] | None, mocker: MockerFixture
) -> None:
    mocker.patch.object(crud.user, "authenticate_by_mail", return_value=user)
    if exc is not None:
        with pytest.raises(exc):
            authenticate_and_authorize_user(mock_db, form_data=Mock())
    else:
        token = authenticate_and_authorize_user(mock_db, form_data=Mock())
        assert isinstance(token, str)


def test_process_reset_password_request_token_should_not_be_created_if_no_user_with_given_email(
    mock_db: Mock, mock_crud_user: Mock, mock_crud_password_reset: Mock, mock_background_tasks: Mock, mock_mailer: Mock
) -> None:
    mock_crud_user.get_by_email.return_value = None
    process_reset_password_request(
        mock_db, password_reset_request=Mock(), background_tasks=mock_background_tasks, mailer=mock_mailer
    )

    mock_crud_password_reset.create.assert_not_called()


@pytest.mark.usefixtures("mock_send_password_reset_request_mail")
def test_process_reset_password_request_should_invalidate_all_other_reset_tokens(
    mock_db: Mock,
    mock_crud_user: Mock,
    mock_crud_password_reset: Mock,
    mock_background_tasks: Mock,
    mock_mailer: Mock,
    mock_current_user: Mock,
) -> None:
    mock_crud_user.get_by_email.return_value = mock_current_user
    process_reset_password_request(
        mock_db, password_reset_request=Mock(), background_tasks=mock_background_tasks, mailer=mock_mailer
    )

    mock_crud_password_reset.invalidate_all.assert_called_once()


@pytest.mark.usefixtures("mock_send_password_reset_request_mail")
def test_process_reset_password_request_should_create_password_reset_token(
    mock_db: Mock,
    mock_crud_user: Mock,
    mock_crud_password_reset: Mock,
    mock_background_tasks: Mock,
    mock_mailer: Mock,
    mock_current_user: Mock,
) -> None:
    mock_crud_user.get_by_email.return_value = mock_current_user
    process_reset_password_request(
        mock_db, password_reset_request=Mock(), background_tasks=mock_background_tasks, mailer=mock_mailer
    )

    mock_crud_password_reset.create.assert_called_once()


@pytest.mark.usefixtures("mock_crud_password_reset")
def test_process_reset_password_request_should_send_email(
    mock_db: Mock,
    mock_crud_user: Mock,
    mock_background_tasks: Mock,
    mock_mailer: Mock,
    mock_current_user: Mock,
    mocker: MockerFixture,
) -> None:
    mock_crud_user.get_by_email.return_value = mock_current_user
    mock_send_email = mocker.patch("app.auth.deps.send_password_reset_request_mail")
    process_reset_password_request(
        mock_db, password_reset_request=Mock(), background_tasks=mock_background_tasks, mailer=mock_mailer
    )

    mock_background_tasks.add_task.assert_called_once_with(mock_mailer.send, mock_send_email())


@pytest.mark.parametrize(
    "token,is_invalidated,is_expired,raise_exception",
    [
        (None, False, False, True),
        (Mock(), True, False, True),
        (Mock(), False, True, True),
        (Mock(), False, False, False),
    ],
)
def test_invalidate_password_reset_token(
    mock_db: Mock,
    mock_crud_password_reset: Mock,
    token: Mock | None,
    is_invalidated: bool,
    is_expired: bool,
    raise_exception: bool,
) -> None:
    mock_crud_password_reset.get_by_value.return_value = token
    mock_crud_password_reset.is_invalidated.return_value = is_invalidated
    mock_crud_password_reset.is_expired.return_value = is_expired

    if raise_exception:
        with pytest.raises(InvalidToken):
            invalidate_password_reset_token(mock_db, password_reset_form=Mock())
    else:
        invalidate_password_reset_token(mock_db, password_reset_form=Mock())
        mock_crud_password_reset.invalidate.assert_called_once()


def test_reset_user_password(mock_db: Mock, mock_crud_user: Mock, mocker: MockerFixture) -> None:
    reset_user_password(mock_db, password_reset_form=Mock(), token=Mock())
    mocker.patch.object(user_exists, "by_id")

    mock_crud_user.change_password.assert_called_once()
