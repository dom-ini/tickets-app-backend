from typing import Sequence

from pydantic import BaseModel
from sqlalchemy import Row, func, select  # type: ignore[attr-defined]
from sqlalchemy.orm import Session

from app.common.crud import CRUDBase
from app.tickets.models import Ticket, TicketCategory
from app.tickets.schemas import TicketCategoryCreate


class CRUDTicketCategory(CRUDBase[TicketCategory, TicketCategoryCreate, BaseModel]):
    def get_all_by_event(
        self, db: Session, *, event_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[Row[TicketCategory, int]]:
        query = (
            select(  # type: ignore[attr-defined]
                self.model,
                (self.model.quota - func.count(Ticket.id)).label("tickets_left"),  # pylint: disable=not-callable
            )
            .outerjoin(Ticket, self.model.id == Ticket.ticket_category_id)  # type: ignore[arg-type]
            .where(self.model.event_id == event_id)
            .group_by(self.model.id)
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(query)
        return result.all()
