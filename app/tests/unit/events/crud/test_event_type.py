from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.events import crud


@pytest.fixture(name="mock_select")
def get_mock_select(mocker: MockerFixture) -> Mock:
    return mocker.patch("app.events.crud.crud_event_type.select", return_value=Mock())


def test_get_by_mail(mock_db: Mock, mock_select: Mock) -> None:
    crud.event_type.get_event_type_tree(mock_db)

    mock_select.assert_called_once_with(crud.event_type.model)
