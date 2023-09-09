from typing import Sequence

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.crud import CRUDBase
from app.tickets.models import TicketCategory
from app.tickets.schemas import TicketCategoryCreate


class CRUDTicketCategory(CRUDBase[TicketCategory, TicketCategoryCreate, BaseModel]):
    def get_all_by_event(
        self, db: Session, *, event_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[TicketCategory]:
        query = select(self.model).where(self.model.event_id == event_id).offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()
