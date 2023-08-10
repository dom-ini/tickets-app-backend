from app.common.utils import InstanceInDBValidator
from app.events import crud
from app.events.crud import CRUDArtist, CRUDEvent
from app.events.exceptions import ArtistNotFound, EventNotFound
from app.events.models import Artist, Event

event_exists = InstanceInDBValidator[Event, CRUDEvent](crud_service=crud.event, exception=EventNotFound())
artist_exists = InstanceInDBValidator[Artist, CRUDArtist](crud_service=crud.artist, exception=ArtistNotFound())
