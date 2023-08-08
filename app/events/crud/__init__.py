from pydantic import BaseModel

from app.common.crud import CRUDBase
from app.events.crud.event import CRUDEvent
from app.events.models import Artist, Event, EventType, Location, Organizer
from app.events.schemas import ArtistCreate, EventTypeCreate, LocationCreate, OrganizerCreate

event = CRUDEvent(Event)
artist = CRUDBase[Artist, ArtistCreate, BaseModel](Artist)
event_type = CRUDBase[EventType, EventTypeCreate, BaseModel](EventType)
location = CRUDBase[Location, LocationCreate, BaseModel](Location)
organizer = CRUDBase[Organizer, OrganizerCreate, BaseModel](Organizer)
