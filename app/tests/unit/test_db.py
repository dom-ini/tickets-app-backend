from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore[attr-defined]

from app.db.base_class import Base
from app.db.init_db import init_db


@pytest.fixture(name="mock_create")
def get_mock_create_user(mocker: MockerFixture) -> Mock:
    return mocker.patch("app.auth.crud.user.create")


def test_init_db_creates_superuser_if_no_superuser_in_db(
    mock_create: Mock, mock_db: Mock, mocker: MockerFixture
) -> None:
    mocker.patch("app.auth.crud.user.get_by_email", return_value=None)
    init_db(mock_db)
    mock_create.assert_called_once()


def test_init_db_does_not_create_superuser_if_superuser_already_in_db(
    mock_create: Mock, mock_db: Mock, mocker: MockerFixture
) -> None:
    mocker.patch("app.auth.crud.user.get_by_email", return_value=Mock())
    init_db(mock_db)
    mock_create.assert_not_called()


def test_base_class_creates_table_name_automatically() -> None:
    class Model(Base):
        id: Mapped[int] = mapped_column(primary_key=True)

    assert Model.__tablename__ == "model"
