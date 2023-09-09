from datetime import datetime
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError

from app.auth import crud
from app.auth.schemas import PasswordResetTokenCreate


def test_create_should_rollback_on_integrity_error(mock_db: Mock) -> None:
    mock_db.commit.side_effect = [IntegrityError("IntegrityError raised", orig=BaseException(), params=None), None]
    obj_in = PasswordResetTokenCreate(user_id=1)

    crud.password_reset_token.create(mock_db, obj_in=obj_in)

    mock_db.rollback.assert_called_once()


def test_create_contains_user_id(mock_db: Mock) -> None:
    user_id = 123
    obj_in = PasswordResetTokenCreate(user_id=user_id)
    token = crud.password_reset_token.create(mock_db, obj_in=obj_in)

    assert token.user_id == user_id


def test_create_expiration_date_is_in_future(mock_db: Mock) -> None:
    obj_in = PasswordResetTokenCreate(user_id=1)
    token = crud.password_reset_token.create(mock_db, obj_in=obj_in)

    assert token.expires_at > datetime.utcnow()


@pytest.mark.parametrize("invalidated", [False, True])
def test_invalidate(mock_db: Mock, invalidated: bool) -> None:
    db_obj = Mock()
    db_obj.is_invalidated = invalidated
    token = crud.password_reset_token.invalidate(mock_db, token=db_obj)

    assert token.is_invalidated


@pytest.mark.parametrize("invalidated", [False, True])
def test_is_invalidated(invalidated: bool) -> None:
    token = Mock()
    token.is_invalidated = invalidated
    result = crud.password_reset_token.is_invalidated(token)

    assert result == invalidated


@pytest.mark.parametrize(
    "expires_at,expected",
    [
        (datetime(2022, 1, 1), True),
        (datetime(2023, 1, 1, 0, 0, 0, 0), True),
        (datetime(2024, 1, 1, 0, 0, 0, 0), False),
    ],
)
def test_is_expired(mocker: MockerFixture, expires_at: datetime, expected: bool) -> None:
    date_to_compare = datetime(2023, 1, 1, 0, 0, 0, 0)
    mock_date = mocker.patch("app.auth.crud.crud_password_reset.datetime")
    mock_date.utcnow.return_value = date_to_compare
    token = Mock()
    token.expires_at = expires_at
    result = crud.password_reset_token.is_expired(token)

    assert result == expected
