import datetime
from typing import Any

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.events.models import Event
from app.tickets import crud
from app.tickets.models import Ticket, TicketCategory
from app.tickets.schemas import TicketCategoryCreate


def create_category(db: Session, quota: int, event: Event) -> TicketCategory:
    category_in = TicketCategoryCreate(name="example", quota=quota, event_id=event.id)
    return crud.ticket_category.create(db, obj_in=category_in)


def modify_event(db: Session, event: Event, attr_name: str, attr_value: Any) -> Event:
    setattr(event, attr_name, attr_value)
    db.add(event)
    db.commit()
    return event


class TestTickets:  # pylint: disable=R0904
    @pytest.fixture()
    def category_with_no_quota(self, db: Session, event: Event) -> TicketCategory:
        return create_category(db, quota=0, event=event)

    @pytest.fixture()
    def category_with_one_ticket(self, db: Session, event: Event) -> TicketCategory:
        return create_category(db, quota=1, event=event)

    @pytest.fixture()
    def category_for_inactive_event(self, db: Session, event: Event) -> TicketCategory:
        inactive_event = modify_event(db, event=event, attr_name="is_active", attr_value=False)
        return create_category(db, quota=10, event=inactive_event)

    @pytest.fixture()
    def category_for_expired_event(self, db: Session, event: Event) -> TicketCategory:
        expired_event = modify_event(db, event=event, attr_name="held_at", attr_value=datetime.datetime(2010, 1, 1))
        return create_category(db, quota=10, event=expired_event)

    def test_get_tickets_by_user_if_user_not_authenticated_should_fail(self, client: TestClient) -> None:
        r = client.get(f"{settings.API_V1_STR}/tickets/")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_tickets_by_user(
        self, client: TestClient, user_tickets: list[Ticket], normal_user_token_headers: dict[str, str]
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/tickets/", headers=normal_user_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == len(user_tickets)

    def test_get_tickets_by_user_and_event_with_invalid_event_id(
        self,
        client: TestClient,
        user_tickets: list[Ticket],  # pylint: disable=W0613
        normal_user_token_headers: dict[str, str],
    ) -> None:
        event_id = 999
        r = client.get(f"{settings.API_V1_STR}/tickets/?event_id={event_id}", headers=normal_user_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == 0

    def test_get_tickets_by_user_and_event(
        self, client: TestClient, event: Event, user_tickets: list[Ticket], normal_user_token_headers: dict[str, str]
    ) -> None:
        event_id = event.id
        print(event.id)
        r = client.get(f"{settings.API_V1_STR}/tickets/?event_id={event_id}", headers=normal_user_token_headers)
        result = r.json()
        print(result)
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == len(user_tickets)

    def test_get_tickets_by_user_pagination(
        self, client: TestClient, user_tickets: list[Ticket], normal_user_token_headers: dict[str, str]
    ) -> None:
        limit = 1
        skip = 1
        r = client.get(f"{settings.API_V1_STR}/tickets/?limit={limit}&skip={skip}", headers=normal_user_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == limit
        assert result[0].get("id") == user_tickets[skip].id

    def test_get_ticket_by_id(
        self, client: TestClient, ticket: Ticket, normal_user_token_headers: dict[str, str]
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/tickets/{ticket.id}", headers=normal_user_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("id") == ticket.id

    def test_get_ticket_by_id_if_user_not_authenticated_should_fail(self, client: TestClient, ticket: Ticket) -> None:
        r = client.get(f"{settings.API_V1_STR}/tickets/{ticket.id}")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_ticket_by_id_if_user_is_not_owner_should_fail(
        self, client: TestClient, ticket: Ticket, superuser_token_headers: dict[str, str]
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/tickets/{ticket.id}", headers=superuser_token_headers)
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_get_ticket_by_wrong_id_should_fail(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        ticket_id = 9999
        r = client.get(f"{settings.API_V1_STR}/tickets/{ticket_id}", headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_reserve_ticket(
        self, client: TestClient, ticket_category: TicketCategory, normal_user_token_headers: dict[str, str]
    ) -> None:
        payload = {"email": "email@example.com", "ticket_category_id": ticket_category.id}
        r = client.post(f"{settings.API_V1_STR}/tickets", json=payload, headers=normal_user_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_201_CREATED
        assert result.get("email") == payload.get("email")
        assert "token" in result

    def test_reserve_ticket_no_more_tickets_left_should_fail(
        self, client: TestClient, category_with_no_quota: TicketCategory, normal_user_token_headers: dict[str, str]
    ) -> None:
        payload = {"email": "email@example.com", "ticket_category_id": category_with_no_quota.id}
        r = client.post(f"{settings.API_V1_STR}/tickets", json=payload, headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_reserve_ticket_if_user_not_authenticated_should_fail(
        self, client: TestClient, ticket_category: TicketCategory
    ) -> None:
        payload = {"email": "email@example.com", "ticket_category_id": ticket_category.id}
        r = client.post(f"{settings.API_V1_STR}/tickets", json=payload)
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_reserve_ticket_wrong_ticket_category_should_fail(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        payload = {"email": "email@example.com", "ticket_category_id": 9999}
        r = client.post(f"{settings.API_V1_STR}/tickets", json=payload, headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_reserve_ticket_inactive_event_should_fail(
        self, client: TestClient, category_for_inactive_event: TicketCategory, normal_user_token_headers: dict[str, str]
    ) -> None:
        payload = {"email": "email@example.com", "ticket_category_id": category_for_inactive_event.id}
        r = client.post(f"{settings.API_V1_STR}/tickets", json=payload, headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_reserve_ticket_expired_event_should_fail(
        self, client: TestClient, category_for_expired_event: TicketCategory, normal_user_token_headers: dict[str, str]
    ) -> None:
        payload = {"email": "email@example.com", "ticket_category_id": category_for_expired_event.id}
        r = client.post(f"{settings.API_V1_STR}/tickets", json=payload, headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_reserve_ticket_if_user_already_has_ticket_for_event_should_fail(
        self, client: TestClient, ticket: Ticket, normal_user_token_headers: dict[str, str]
    ) -> None:
        payload = {"email": "email@example.com", "ticket_category_id": ticket.ticket_category_id}
        r = client.post(f"{settings.API_V1_STR}/tickets", json=payload, headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_resign_from_ticket(
        self, client: TestClient, ticket: Ticket, normal_user_token_headers: dict[str, str]
    ) -> None:
        request1 = client.delete(f"{settings.API_V1_STR}/tickets/{ticket.id}", headers=normal_user_token_headers)
        request2 = client.get(f"{settings.API_V1_STR}/tickets/{ticket.id}", headers=normal_user_token_headers)
        assert request1.status_code == status.HTTP_200_OK
        assert request2.status_code == status.HTTP_404_NOT_FOUND

    def test_resign_from_ticket_if_user_not_authenticated_should_fail(self, client: TestClient, ticket: Ticket) -> None:
        r = client.delete(f"{settings.API_V1_STR}/tickets/{ticket.id}")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_resign_from_ticket_if_ticket_does_not_exist_should_fail(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        ticket_id = 9999
        r = client.delete(f"{settings.API_V1_STR}/tickets/{ticket_id}", headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_resign_from_ticket_if_user_is_not_owner_should_fail(
        self, client: TestClient, ticket: Ticket, superuser_token_headers: dict[str, str]
    ) -> None:
        r = client.delete(f"{settings.API_V1_STR}/tickets/{ticket.id}", headers=superuser_token_headers)
        assert r.status_code == status.HTTP_404_NOT_FOUND
