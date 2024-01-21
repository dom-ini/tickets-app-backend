from datetime import datetime

import pytest
from _pytest.fixtures import FixtureRequest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import models as auth_models
from app.core.config import settings
from app.events import crud, models, schemas

EVENT_COUNT = 3


class TestEvents:
    @pytest.fixture(name="multiple_events")
    def create_multiple_events(  # pylint: disable=R0913
        self,
        db: Session,
        location: models.Location,
        organizer: models.Organizer,
        event_type: models.EventType,
        speaker: models.Speaker,
        superuser: auth_models.User,
    ) -> list[models.Event]:
        events = []
        for i in range(EVENT_COUNT):
            event_in = schemas.EventCreate(
                name=f"Event{i}",
                description="Description",
                slug=f"event{i}",
                held_at=datetime.now(),
                location_id=location.id,
                organizer_id=organizer.id,
                event_type_id=event_type.id,
                created_by_id=superuser.id,
            )
            event = crud.event.create(db, obj_in=event_in)
            crud.event.add_speaker(db, event=event, speaker=speaker)
            events.append(event)
        return events

    def test_list_events(self, client: TestClient, event: models.Event) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert all(k in result for k in ["items", "total_count"])
        assert len(result["items"]) == result["total_count"] == 1
        assert result["items"][0].get("id") == event.id

    def test_list_events_pagination(self, client: TestClient, multiple_events: list[models.Event]) -> None:
        limit = 2
        skip = 1
        r = client.get(f"{settings.API_V1_STR}/events/?limit={limit}&skip={skip}&sort_by=id")
        result = r.json()["items"]
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == min(EVENT_COUNT, limit)
        assert result[0].get("id") == multiple_events[skip].id

    @pytest.mark.parametrize(
        "filter_,expected_count",
        [
            ("name__icontains=event", EVENT_COUNT),
            ("name__icontains=not", 0),
            ("held_at__gte=2020-01-01", EVENT_COUNT),
            ("held_at__gte=2025-01-01", 0),
            ("held_at__lte=2025-01-01", EVENT_COUNT),
            ("held_at__lte=2020-01-01", 0),
            (f"slug__exact=event{EVENT_COUNT - 1}", 1),
            ("slug__exact=not-slug", 0),
            ("event_type_id__exact=999", 0),
            ("location_id__exact=999", 0),
        ],
    )
    @pytest.mark.usefixtures("multiple_events")
    def test_list_events_filtering(
        self,
        client: TestClient,
        filter_: str,
        expected_count: int,
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/?{filter_}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result["total_count"] == expected_count

    @pytest.mark.parametrize(
        "filter_name,related_instance,expected_count",
        [
            ("speakers__id__exact", "speaker", EVENT_COUNT),
            ("speakers__id__exact", None, 0),
            ("location__name__icontains", "location", EVENT_COUNT),
            ("location__name__icontains", None, 0),
            ("location__city__icontains", "location", EVENT_COUNT),
            ("location__city__icontains", None, 0),
        ],
    )
    @pytest.mark.usefixtures("multiple_events")
    def test_list_events_filtering_by_relationship(  # pylint: disable=R0913
        self,
        client: TestClient,
        filter_name: str,
        related_instance: str,
        expected_count: int,
        request: FixtureRequest,
    ) -> None:
        lookup_field = filter_name.split("__")[1]
        filter_value = getattr(request.getfixturevalue(related_instance), lookup_field) if related_instance else 0
        r = client.get(f"{settings.API_V1_STR}/events/?{filter_name}={filter_value}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result["total_count"] == expected_count

    def test_list_events_sorting_by_wrong_field_should_fail(self, client: TestClient) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/?sort_by=invalid_field")
        assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_events_sorting_ascending(self, client: TestClient, multiple_events: list[models.Event]) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/?sort_by=held_at")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result["total_count"] == len(multiple_events)
        assert result["items"] == sorted(result["items"], key=lambda event: event["held_at"])

    def test_list_events_sorting_descending(self, client: TestClient, multiple_events: list[models.Event]) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/?sort_by=-held_at")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result["total_count"] == len(multiple_events)
        assert result["items"] == sorted(result["items"], key=lambda event: event["held_at"], reverse=True)

    def test_list_events_filter_by_valid_event_type_id(
        self, client: TestClient, multiple_events: list[models.Event]
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/?event_type_id__exact={multiple_events[0].event_type_id}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result["total_count"] == EVENT_COUNT

    def test_list_events_filter_by_valid_location_type_id(
        self, client: TestClient, multiple_events: list[models.Event]
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/?location_id__exact={multiple_events[0].location_id}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result["total_count"] == EVENT_COUNT

    @pytest.mark.usefixtures("multiple_events", "ticket_category")
    def test_list_events_only_with_available_tickets(
        self,
        client: TestClient,
        event: models.Event,
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/?only_with_available_tickets=true")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result["total_count"] == 1
        assert result["items"][0].get("id") == event.id

    def test_get_event_by_slug(self, client: TestClient, event: models.Event) -> None:
        r = client.get(f"{settings.API_V1_STR}/events/{event.slug}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("slug") == event.slug

    def test_get_event_by_wrong_slug_should_fail(self, client: TestClient) -> None:
        event_slug = "wrong-slug"
        r = client.get(f"{settings.API_V1_STR}/events/{event_slug}")
        assert r.status_code == status.HTTP_404_NOT_FOUND
