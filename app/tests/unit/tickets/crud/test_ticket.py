import random
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.tickets import crud
from app.tickets.schemas import TicketCreate


@pytest.fixture(name="mock_get_by_token")
def get_mock_by_token(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch.object(crud.ticket, "get_by_token")
    return mocked


@pytest.fixture(name="mock_create")
def get_mock_create(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch.object(crud.ticket, "create")
    return mocked


def test_create_token_generation_does_not_rely_on_seed(mock_db: Mock, mock_get_by_token: Mock) -> None:
    random.seed(0)
    mock_get_by_token.return_value = None
    ticket_in = TicketCreate(email="email@example.com", ticket_category_id=1, user_id=1)
    ticket1 = crud.ticket.create(mock_db, obj_in=ticket_in)
    ticket2 = crud.ticket.create(mock_db, obj_in=ticket_in)

    assert ticket1.token != ticket2.token


def test_create_token_is_regenerated_if_is_not_unique(mock_db: Mock, mock_get_by_token: Mock) -> None:
    mock_get_by_token.side_effect = [Mock(), None]
    ticket_in = TicketCreate(email="email@example.com", ticket_category_id=1, user_id=1)
    crud.ticket.create(mock_db, obj_in=ticket_in)

    assert mock_get_by_token.call_count == 2
