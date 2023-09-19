from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.auth import models as auth_models
from app.events import crud, models, schemas


class TestEvent:
    def test_create_event(  # pylint: disable=R0913
        self,
        db: Session,
        location: models.Location,
        organizer: models.Organizer,
        event_type: models.EventType,
        superuser: auth_models.User,
    ) -> None:
        fields = {
            "name": "event",
            "description": "description",
            "slug": "event-slug",
            "held_at": datetime.now(),
        }
        event_in = schemas.EventCreate(
            **fields,
            location_id=location.id,
            organizer_id=organizer.id,
            event_type_id=event_type.id,
            created_by_id=superuser.id,
        )
        event = crud.event.create(db, obj_in=event_in)
        assert all(getattr(event, field) == value for field, value in fields.items())
        assert event.location.id == location.id
        assert event.organizer.id == organizer.id
        assert event.event_type.id == event_type.id

    def test_get_by_slug(self, db: Session, event: models.Event) -> None:
        event2 = crud.event.get_by_slug(db, slug=event.slug)
        assert event2 is not None
        assert event2.id == event.id

    def test_add_speaker_to_event(self, db: Session, event: models.Event, speaker: models.Speaker) -> None:
        crud.event.add_speaker(db, event=event, speaker=speaker)
        speakers = crud.event.speakers(event)
        assert len(speakers) == 1
        assert speakers[0].id == speaker.id

    def test_remove_speaker_from_event(self, db: Session, event: models.Event, speaker: models.Speaker) -> None:
        crud.event.add_speaker(db, event=event, speaker=speaker)
        crud.event.remove_speaker(db, event=event, speaker=speaker)
        speakers = crud.event.speakers(event)
        assert len(speakers) == 0

    def test_remove_event(self, db: Session, event: models.Event) -> None:
        crud.event.remove(db, id_=event.id)
        event3 = crud.event.get(db, id_=event.id)
        assert event3 is None

    @pytest.mark.parametrize("is_active", [True, False])
    def test_is_active(self, event: models.Event, is_active: bool) -> None:
        event.is_active = is_active
        assert crud.event.is_active(event) == is_active

    @pytest.mark.parametrize("held_at,expected", [(datetime(2010, 1, 1), True), (datetime(2040, 1, 1), False)])
    def test_is_expired(self, event: models.Event, held_at: datetime, expected: bool) -> None:
        event.held_at = held_at
        assert crud.event.is_expired(event) == expected
