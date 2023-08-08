from datetime import datetime

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
            "poster_vertical": "https://example.com/",
            "poster_horizontal": "https://example.com/",
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

    def test_add_artist_to_event(self, db: Session, event: models.Event, artist: models.Artist) -> None:
        crud.event.add_artist(db, event=event, artist=artist)
        artists = crud.event.artists(event)
        assert len(artists) == 1
        assert artists[0].id == artist.id

    def test_remove_artist_from_event(self, db: Session, event: models.Event, artist: models.Artist) -> None:
        crud.event.add_artist(db, event=event, artist=artist)
        crud.event.remove_artist(db, event=event, artist=artist)
        artists = crud.event.artists(event)
        assert len(artists) == 0

    def test_remove_event(self, db: Session, event: models.Event) -> None:
        crud.event.remove(db, id_=event.id)
        event3 = crud.event.get(db, id_=event.id)
        assert event3 is None
