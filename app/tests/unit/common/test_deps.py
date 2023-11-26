from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status
from jose import jwt
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from app.common.deps import (
    DEFAULT_PAGE_OFFSET,
    DEFAULT_PAGE_SIZE,
    PaginationParams,
    get_current_active_superuser,
    get_current_active_user,
    get_current_user,
    get_db,
)
from app.core.config import settings

MockCrudUser = dict[str, Mock]


@pytest.fixture(name="mock_crud_user")
def get_mock_crud_user(mocker: MockerFixture) -> MockCrudUser:
    mocks = {
        "get": mocker.patch("app.auth.crud.user.get"),
        "is_disabled": mocker.patch("app.auth.crud.user.is_disabled"),
        "is_activated": mocker.patch("app.auth.crud.user.is_activated"),
        "is_superuser": mocker.patch("app.auth.crud.user.is_superuser"),
    }
    return mocks


@pytest.fixture(name="mock_current_user")
def get_mock_current_user() -> Mock:
    return Mock()


def test_get_db() -> None:
    db = next(get_db())
    assert db is not None
    assert isinstance(db, Session)


def test_pagination_params_init() -> None:
    skip = 10
    limit = 10

    pagination = PaginationParams(skip=skip, limit=limit)

    assert pagination.skip == skip
    assert pagination.limit == limit


def test_pagination_params_set_to_0_if_negative_values_given() -> None:
    skip = -10
    limit = -10

    pagination = PaginationParams(skip=skip, limit=limit)

    assert pagination.skip == pagination.limit == 0


def test_pagination_params_default_values() -> None:
    pagination = PaginationParams()

    assert pagination.skip == DEFAULT_PAGE_OFFSET
    assert pagination.limit == DEFAULT_PAGE_SIZE


def test_get_current_user_valid_token(mock_db: Mock, mock_crud_user: MockCrudUser) -> None:
    token = "valid-token"
    token_payload = {"sub": "user_id"}

    with patch("app.common.deps.jwt.decode", return_value=token_payload) as mock_decode:
        user = get_current_user(mock_db, token)

        mock_decode.assert_called_once_with(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        mock_crud_user["get"].assert_called_once_with(mock_db, id_=token_payload["sub"])
        assert user == mock_crud_user["get"].return_value


def test_get_current_user_invalid_token_should_fail(mock_db: Mock) -> None:
    token = "invalid-token"

    with patch("app.common.deps.jwt.decode", side_effect=jwt.JWTError):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_db, token=token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_invalid_user_id_should_fail(mock_db: Mock, mock_crud_user: MockCrudUser) -> None:
    token = "valid-token"
    token_payload = {"sub": "invalid_user_id"}
    mock_crud_user["get"].return_value = None

    with patch("app.common.deps.jwt.decode", return_value=token_payload):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_db, token=token)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_get_current_active_user(mock_crud_user: MockCrudUser, mock_current_user: Mock) -> None:
    mock_crud_user["is_activated"].return_value = True
    mock_crud_user["is_disabled"].return_value = False

    user = get_current_active_user(mock_current_user)

    mock_crud_user["is_activated"].assert_called_once_with(mock_current_user)
    mock_crud_user["is_disabled"].assert_called_once_with(mock_current_user)
    assert user == mock_current_user


@pytest.mark.parametrize("is_disabled, is_activated", [(False, False), (True, True)])
def test_get_current_active_user_not_activated_user_should_fail(  # pylint: disable=R0913
    mock_crud_user: MockCrudUser, mock_current_user: Mock, is_disabled: bool, is_activated: bool
) -> None:
    mock_crud_user["is_activated"].return_value = is_activated
    mock_crud_user["is_disabled"].return_value = is_disabled

    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(mock_current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


def test_get_current_active_superuser(mock_crud_user: MockCrudUser, mock_current_user: Mock) -> None:
    mock_crud_user["is_superuser"].return_value = True

    user = get_current_active_superuser(mock_current_user)

    mock_crud_user["is_superuser"].assert_called_once_with(mock_current_user)
    assert user == mock_current_user


def test_get_current_active_superuser_not_superuser_should_fail(
    mock_crud_user: MockCrudUser, mock_current_user: Mock
) -> None:
    mock_crud_user["is_superuser"].return_value = False

    with pytest.raises(HTTPException) as exc_info:
        get_current_active_superuser(mock_current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
