from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.crud import CRUDBase, SlugMixin
from app.common.schemas import EmptySchema
from app.events.models import EventType
from app.events.schemas import EventTypeCreate


class CRUDEventType(CRUDBase[EventType, EventTypeCreate, EmptySchema], SlugMixin[EventType]):
    def get_event_type_tree(self, db: Session) -> Sequence[EventType]:
        query = select(self.model).where(self.model.parent_type_id.is_(None))
        result = db.execute(query)
        event_types = result.scalars().all()
        return event_types
