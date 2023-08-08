from app.common.deps import DBSession
from app.common.utils import validate_instance_id
from app.events import crud, models
from app.events.exceptions import ArtistNotFound, EventNotFound


def valid_event_id(db: DBSession, event_id: int) -> models.Event:
    event = validate_instance_id(db, id_=event_id, crud_service=crud.event, not_found_exception=EventNotFound())
    return event


def valid_artist_id(db: DBSession, artist_id: int) -> models.Artist:
    artist = validate_instance_id(db, id_=artist_id, crud_service=crud.artist, not_found_exception=ArtistNotFound())
    return artist
