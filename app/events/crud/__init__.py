from pydantic import BaseModel

from app.common.crud import CRUDBase
from app.events.crud.crud_event import CRUDEvent
from app.events.crud.crud_event_type import CRUDEventType
from app.events.crud.crud_speaker import CRUDSpeaker
from app.events.models import Event, EventType, Location, Organizer, Speaker
from app.events.schemas import LocationCreate, OrganizerCreate

CRUDLocation = CRUDBase[Location, LocationCreate, BaseModel]
CRUDOrganizer = CRUDBase[Organizer, OrganizerCreate, BaseModel]

event = CRUDEvent(Event)
speaker = CRUDSpeaker(Speaker)
event_type = CRUDEventType(EventType)
location = CRUDLocation(Location)
organizer = CRUDOrganizer(Organizer)
