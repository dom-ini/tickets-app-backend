from app.common.utils import InstanceInDBValidator
from app.events import crud
from app.events.crud import CRUDEvent, CRUDSpeaker
from app.events.exceptions import EventNotFound, SpeakerNotFound
from app.events.models import Event, Speaker

event_exists = InstanceInDBValidator[Event, CRUDEvent](crud_service=crud.event, exception=EventNotFound())
speaker_exists = InstanceInDBValidator[Speaker, CRUDSpeaker](crud_service=crud.speaker, exception=SpeakerNotFound())
