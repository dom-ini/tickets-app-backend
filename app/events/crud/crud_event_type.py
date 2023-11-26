from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

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

    def get_event_type_parent_hierarchy(self, db: Session, event_type_id: int) -> Sequence:
        base_query = select(self.model).where(self.model.id == event_type_id).cte(recursive=True)
        parents = aliased(base_query)
        event_type_table = aliased(self.model)
        query = base_query.union_all(
            select(event_type_table).join(  # type: ignore[arg-type]
                parents, event_type_table.id == parents.c.parent_type_id  # type: ignore[arg-type]
            )  # type: ignore[arg-type]
        )
        stmt = select(query)  # type: ignore[arg-type]
        result = db.execute(stmt)
        event_types = result.all()
        return event_types
