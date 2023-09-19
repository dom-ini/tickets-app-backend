from datetime import datetime
from typing import Any, Sequence, Type

import pytest

from app.db.base_class import Base
from app.events.models import Event, EventType, Location, Organizer, Speaker


@pytest.mark.parametrize(
    "model,payload,attrs_in_str",
    [
        (
            Event,
            {
                "name": "event-name",
                "slug": "event-slug",
                "held_at": datetime.utcnow(),
                "organizer_id": 1,
                "created_by_id": 1,
                "event_type_id": 1,
                "location_id": 1,
            },
            ("name", "held_at"),
        ),
        (Organizer, {"name": "organizer-name"}, ("name",)),
        (
            EventType,
            {
                "name": "event-type-name",
                "slug": "event-type-slug",
            },
            ("name",),
        ),
        (
            Location,
            {
                "name": "location-name",
                "slug": "location-slug",
                "city": "location-city",
                "latitude": 11.111,
                "longitude": 22.222,
            },
            ("name", "city"),
        ),
        (
            Speaker,
            {
                "name": "speaker-name",
                "slug": "speaker-slug",
            },
            ("name",),
        ),
    ],
)
def test_str_event_models(model: Type[Base], payload: dict[str, Any], attrs_in_str: Sequence[str]) -> None:
    instance = model(**payload)
    assert all(str(payload.get(key)) in str(instance) for key in attrs_in_str)
