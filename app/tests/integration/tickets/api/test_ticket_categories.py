from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.events.models import Event
from app.tickets.models import TicketCategory


class TestTicketCategories:
    def test_get_ticket_categories_by_event(
        self, client: TestClient, ticket_categories: list[TicketCategory], event: Event
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/ticket-categories/?event_id={event.id}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == len(ticket_categories)

    def test_get_ticket_categories_by_event_with_invalid_event_id(self, client: TestClient) -> None:
        event_id = 9999
        r = client.get(f"{settings.API_V1_STR}/ticket-categories/?event_id={event_id}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == 0

    def test_get_ticket_categories_by_event_pagination(
        self, client: TestClient, ticket_categories: list[TicketCategory], event: Event
    ) -> None:
        limit = 1
        skip = 1
        r = client.get(f"{settings.API_V1_STR}/ticket-categories/?event_id={event.id}&limit={limit}&skip={skip}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == limit
        assert result[0]["ticket_category"].get("id") == ticket_categories[skip].id
