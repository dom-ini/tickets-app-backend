from pydantic import BaseModel

from app.common.crud import CRUDBase
from app.events.crud.crud_artist import CRUDArtist
from app.events.crud.crud_event import CRUDEvent
from app.events.crud.crud_event_type import CRUDEventType
from app.events.models import Artist, Event, EventType, Location, Organizer
from app.events.schemas import LocationCreate, OrganizerCreate

CRUDLocation = CRUDBase[Location, LocationCreate, BaseModel]
CRUDOrganizer = CRUDBase[Organizer, OrganizerCreate, BaseModel]

event = CRUDEvent(Event)
artist = CRUDArtist(Artist)
event_type = CRUDEventType(EventType)
location = CRUDLocation(Location)
organizer = CRUDOrganizer(Organizer)
