from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl

from app.events.schemas.event_type import EventType
from app.events.schemas.location import Location, SimpleLocation
from app.events.schemas.organizer import Organizer
from app.events.schemas.speaker import Speaker


class EventBase(BaseModel):
    name: str
    description: str | None
    slug: str
    poster_vertical: HttpUrl | None = None
    poster_horizontal: HttpUrl | None = None
    is_active: bool = True
    held_at: datetime


class EventInDBase(EventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class EventBrief(EventInDBase):
    location: SimpleLocation


class EventDetails(EventInDBase):
    location: Location
    organizer: Organizer
    event_type: EventType
    speakers: list[Speaker] | None = None


class EventCreate(EventBase):
    location_id: int
    organizer_id: int
    event_type_id: int
    created_by_id: int
