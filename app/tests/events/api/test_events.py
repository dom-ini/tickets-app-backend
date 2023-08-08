from datetime import datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.events import crud, models, schemas


class TestEvents:
    EVENT_COUNT = 3

    @pytest.fixture(name="multiple_events")
    def create_multiple_events(
        self, db: Session, location: models.Location, organizer: models.Organizer, event_type: models.EventType
    ) -> list[models.Event]:
        events = []
        for i in range(self.EVENT_COUNT):
            event_in = schemas.EventCreate(
                name=f"Event{i}",
                description="Description",
                slug=f"event{i}",
                held_at=datetime.now(),
                location_id=location.id,
                organizer_id=organizer.id,
                event_type_id=event_type.id,
            )
            event = crud.event.create(db, obj_in=event_in)
            events.append(event)
        return events

    def test_list_events(self, client: TestClient, event: models.Event) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == 1
        assert result[0].get("id") == event.id

    def test_list_events_pagination(self, client: TestClient, multiple_events: list[models.Event]) -> None:
        limit = 2
        skip = 1
        r = client.get(f"{settings.API_V1_STR}/events/?limit={limit}&skip={skip}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == min(self.EVENT_COUNT, limit)
        assert result[0].get("id") == multiple_events[skip].id

    def test_get_event_by_id(self, client: TestClient, event: models.Event) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/{event.id}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("id") == event.id

    def test_get_event_by_wrong_id_should_fail(self, client: TestClient) -> None:
        event_id = 9999
        r = client.get(f"{settings.API_V1_STR}/events/{event_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND
