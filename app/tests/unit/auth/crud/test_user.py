from typing import Any, Callable
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.auth import crud, schemas


def test_create_hashes_password(mock_db: Mock) -> None:
    password = "Test1234!"
    obj_in = schemas.UserCreate(email="email@example.com", password=password)

    result = crud.user.create(mock_db, obj_in=obj_in)

    assert result.hashed_password != password


def test_update_saves_lowercase_email(mock_db: Mock) -> None:
    email = "EMAIL@example.com"
    obj_in = schemas.UserUpdate(email=email)
    db_obj = Mock()

    result = crud.user.update(mock_db, db_obj=db_obj, obj_in=obj_in)

    assert result.email == email.lower()


def test_change_password_hashes_password(mock_db: Mock) -> None:
    password = "Test1234!"
    db_obj = Mock()

    result = crud.user.change_password(mock_db, user=db_obj, new_password=password)

    assert result.hashed_password != password


@pytest.mark.parametrize(
    "get_return,crud_method,attr,expected",
    [
        (Mock(), "deactivate", "is_disabled", True),
        (None, "deactivate", None, None),
        (Mock(), "activate", "is_activated", True),
        (None, "activate", None, None),
    ],
)
def test_activate_deactivate(  # pylint: disable=R0913
    mock_db: Mock,
    mocker: MockerFixture,
    get_return: Mock | None,
    crud_method: str,
    attr: str | None,
    expected: bool | None,
) -> None:
    mocker.patch.object(crud.user, "get", return_value=get_return)
    method = getattr(crud.user, crud_method)
    user = method(mock_db, user_id=1)
    result = getattr(user, attr) if attr else user

    assert result == expected


@pytest.mark.parametrize(
    "user,password_valid,assert_function",
    [
        (Mock(), True, lambda x: x is not None),
        (None, True, lambda x: x is None),
        (Mock(), False, lambda x: x is None),
    ],
)
def test_authenticate_by_mail(
    mock_db: Mock,
    mocker: MockerFixture,
    user: Mock | None,
    password_valid: bool,
    assert_function: Callable[[Any], bool],
) -> None:
    mocker.patch.object(crud.user, "get_by_email", return_value=user)
    mocker.patch("app.auth.crud.crud_user.verify_password", return_value=password_valid)
    result = crud.user.authenticate_by_mail(mock_db, email="email", password="password")

    assert assert_function(result)


@pytest.mark.parametrize(
    "attr_name,attr_value",
    [
        ("is_disabled", True),
        ("is_disabled", False),
        (
            "is_activated",
            True,
        ),
        ("is_activated", False),
        (
            "is_superuser",
            True,
        ),
        ("is_superuser", False),
    ],
)
def test_boolean_getters(attr_name: str, attr_value: bool) -> None:
    user = Mock()
    setattr(user, attr_name, attr_value)
    function = getattr(crud.user, attr_name)

    assert function(user) == attr_value
