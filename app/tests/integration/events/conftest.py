from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.auth import models as auth_models
from app.events import crud, models, schemas


@pytest.fixture(name="location")
def create_location(db: Session) -> models.Location:
    location_in = schemas.LocationCreate(
        name="Location", city="New York", slug="location", latitude=50.0, longitude=18.0
    )
    return crud.location.create(db, obj_in=location_in)


@pytest.fixture(name="organizer")
def create_organizer(db: Session) -> models.Organizer:
    organizer_in = schemas.OrganizerCreate(name="Organizer")
    return crud.organizer.create(db, obj_in=organizer_in)


@pytest.fixture(name="event_type")
def create_event_type(db: Session) -> models.EventType:
    event_type_in = schemas.EventTypeCreate(name="event type", slug="event-type")
    return crud.event_type.create(db, obj_in=event_type_in)


@pytest.fixture(name="event")
def create_event(
    db: Session,
    location: models.Location,
    organizer: models.Organizer,
    event_type: models.EventType,
    superuser: auth_models.User,
) -> models.Event:
    event_in = schemas.EventCreate(
        name="Event",
        description="Description",
        slug="event",
        held_at=datetime.now(),
        location_id=location.id,
        organizer_id=organizer.id,
        event_type_id=event_type.id,
        created_by_id=superuser.id,
    )
    return crud.event.create(db, obj_in=event_in)


@pytest.fixture(name="artist")
def create_artist(db: Session) -> models.Artist:
    artist_in = schemas.ArtistCreate(name="Artist", description="Description", slug="artist")
    return crud.artist.create(db, obj_in=artist_in)
