from app.common.utils import InstanceInDBValidator
from app.events import crud
from app.events.crud import CRUDEvent, CRUDEventType, CRUDLocation, CRUDSpeaker
from app.events.exceptions import EventNotFound, EventTypeNotFound, LocationNotFound, SpeakerNotFound
from app.events.models import Event, EventType, Location, Speaker

event_exists = InstanceInDBValidator[Event, CRUDEvent](crud_service=crud.event, exception=EventNotFound())
event_type_exists = InstanceInDBValidator[EventType, CRUDEventType](
    crud_service=crud.event_type, exception=EventTypeNotFound()
)
location_exists = InstanceInDBValidator[Location, CRUDLocation](
    crud_service=crud.location, exception=LocationNotFound()
)
speaker_exists = InstanceInDBValidator[Speaker, CRUDSpeaker](crud_service=crud.speaker, exception=SpeakerNotFound())
