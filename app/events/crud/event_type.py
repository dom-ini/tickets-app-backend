from app.common.crud import CRUDBase, SlugMixin
from app.common.schemas import EmptySchema
from app.events.models import EventType
from app.events.schemas import EventTypeCreate


class CRUDEventType(CRUDBase[EventType, EventTypeCreate, EmptySchema], SlugMixin[EventType]):
    pass
