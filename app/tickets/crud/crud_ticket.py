import secrets
from typing import Sequence

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.crud import CRUDBase
from app.tickets.models import Ticket, TicketCategory
from app.tickets.schemas.ticket import TicketCreate


class CRUDTicket(CRUDBase[Ticket, TicketCreate, BaseModel]):
    def get_by_token(self, db: Session, token: str) -> Ticket | None:
        query = select(self.model).where(self.model.token == token)
        result = db.execute(query)
        return result.scalar()

    def get_all_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Ticket]:
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .join(self.model.ticket_category)
            .join(TicketCategory.event)
        )
        result = db.execute(query)
        return result.scalars().all()

    def get_by_category_and_user(self, db: Session, *, user_id: int, ticket_category_id: int) -> Sequence[Ticket]:
        event_query = select(TicketCategory.event_id).where(TicketCategory.id == ticket_category_id)
        ticket_categories_query = select(TicketCategory.id).where(TicketCategory.event_id.in_(event_query))
        query = (
            select(self.model)
            .where(self.model.ticket_category_id.in_(ticket_categories_query))
            .where(self.model.user_id == user_id)
        )
        result = db.execute(query)
        return result.scalars().all()

    def get_by_event_and_user(
        self, db: Session, *, user_id: int, event_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[Ticket]:
        ticket_categories_query = select(TicketCategory.id).where(TicketCategory.event_id == event_id)
        query = (
            (
                select(self.model)
                .where(self.model.ticket_category_id.in_(ticket_categories_query))
                .where(self.model.user_id == user_id)
            )
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(query)
        return result.scalars().all()

    def create(self, db: Session, *, obj_in: TicketCreate) -> Ticket:
        while True:
            token = secrets.token_urlsafe(24)
            ticket_by_url = self.get_by_token(db, token=token)
            if ticket_by_url is None:
                break
        ticket = self.model(**obj_in.model_dump(), token=token)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    def get_count_for_ticket_category(self, db: Session, *, ticket_category_id: int) -> int:
        query = select(func.count(self.model.id)).where(  # pylint: disable=not-callable
            self.model.ticket_category_id == ticket_category_id
        )
        result = db.execute(query)
        return result.scalar()
