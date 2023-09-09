from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.tickets import crud
from app.tickets.deps import (
    reserve_ticket_if_available,
    ticket_belongs_to_user,
    ticket_category_exists,
    validate_ticket_payload,
)
from app.tickets.exceptions import NoMoreTicketsLeft, TicketAlreadyReserved, TicketCategoryNotFound, TicketNotFound
from app.tickets.schemas import TicketCreateBody


@pytest.fixture(name="mock_user")
def get_mock_user() -> Mock:
    return Mock()


@pytest.fixture(name="mock_ticket")
def get_mock_ticket() -> Mock:
    return Mock()


@pytest.fixture(name="ticket_payload")
def get_ticket_payload() -> TicketCreateBody:
    return TicketCreateBody(email="email@example.com", ticket_category_id=1)


@pytest.fixture(name="mock_crud")
def get_mock_crud(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch.object(crud, "ticket")
    return mocked


def test_ticket_belongs_to_user_should_raise_error_if_user_does_not_match(mock_user: Mock, mock_ticket: Mock) -> None:
    user_id = 1
    mock_user.id = user_id
    mock_ticket.user_id = 123
    with pytest.raises(TicketNotFound):
        ticket_belongs_to_user(user=mock_user, ticket=mock_ticket)


def test_ticket_belongs_to_user_returns_ticket_if_user_matches(mock_user: Mock, mock_ticket: Mock) -> None:
    user_id = 1
    mock_user.id = user_id
    mock_ticket.user_id = user_id
    ticket = ticket_belongs_to_user(user=mock_user, ticket=mock_ticket)

    assert ticket == mock_ticket


def test_validate_ticket_payload_should_raise_error_if_category_does_not_exist(
    mock_db: Mock, mock_user: Mock, ticket_payload: TicketCreateBody, mocker: MockerFixture
) -> None:
    mocker.patch.object(ticket_category_exists, "by_id", side_effect=TicketCategoryNotFound)
    with pytest.raises(TicketCategoryNotFound):
        validate_ticket_payload(mock_db, ticket_body=ticket_payload, user=mock_user)


def test_validate_ticket_payload_should_raise_error_if_user_already_has_ticket_for_event(
    mock_db: Mock, mock_user: Mock, ticket_payload: TicketCreateBody, mock_crud: Mock
) -> None:
    mock_crud.get_by_ticket_category_and_user.return_value = Mock()
    with pytest.raises(TicketAlreadyReserved):
        validate_ticket_payload(mock_db, ticket_body=ticket_payload, user=mock_user)


def test_validate_ticket_payload_should_return_payload(
    mock_db: Mock, mock_user: Mock, ticket_payload: TicketCreateBody, mock_crud: Mock, mocker: MockerFixture
) -> None:
    mocker.patch.object(ticket_category_exists, "by_id")
    mock_crud.get_by_ticket_category_and_user.return_value = None
    result = validate_ticket_payload(mock_db, ticket_body=ticket_payload, user=mock_user)

    assert result == ticket_payload


def test_reserve_ticket_if_available_should_raise_error_if_category_does_not_exist(
    mock_db: Mock,
    mock_user: Mock,
    ticket_payload: TicketCreateBody,
    mocker: MockerFixture,
) -> None:
    mock_user.id = 1
    mocker.patch.object(crud.ticket_category, "get", return_value=None)

    with pytest.raises(TicketCategoryNotFound):
        reserve_ticket_if_available(mock_db, ticket_data=ticket_payload, user=mock_user)


@pytest.mark.parametrize(
    "tickets_quota, tickets_reserved, expected_exception",
    [(2, 2, NoMoreTicketsLeft), (2, 1, None)],
)
def test_reserve_ticket_if_available(  # pylint: disable=R0913
    mock_db: Mock,
    mock_user: Mock,
    ticket_payload: TicketCreateBody,
    mock_crud: Mock,
    mock_ticket: Mock,
    mocker: MockerFixture,
    tickets_quota: int,
    tickets_reserved: int,
    expected_exception: Exception | None,
) -> None:
    mock_user.id = 1
    mock_category = Mock()
    mock_category.quota = tickets_quota
    mocker.patch.object(crud.ticket_category, "get", return_value=mock_category)
    mock_crud.get_count_for_ticket_category.return_value = tickets_reserved
    mock_crud.create.return_value = mock_ticket

    if expected_exception:
        with pytest.raises(NoMoreTicketsLeft):
            reserve_ticket_if_available(mock_db, ticket_data=ticket_payload, user=mock_user)
    else:
        ticket = reserve_ticket_if_available(mock_db, ticket_data=ticket_payload, user=mock_user)
        assert ticket == mock_ticket
