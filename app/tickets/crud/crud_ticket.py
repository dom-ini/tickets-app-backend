import secrets
from typing import Sequence

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.crud import CRUDBase
from app.tickets.models import Ticket
from app.tickets.schemas.ticket import TicketCreate

MAX_NO_OF_RESERVE_RETRIES = 3


class CRUDTicket(CRUDBase[Ticket, TicketCreate, BaseModel]):
    def get_by_token(self, db: Session, token: str) -> Ticket | None:
        query = select(self.model).where(self.model.token == token)
        result = db.execute(query)
        return result.scalar()

    def get_all_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Ticket]:
        query = select(self.model).where(self.model.user_id == user_id).offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()

    def get_by_ticket_category_and_user(self, db: Session, *, user_id: int, ticket_category_id: int) -> Ticket | None:
        query = select(self.model).where(
            (self.model.user_id == user_id) & (self.model.ticket_category_id == ticket_category_id)
        )
        result = db.execute(query)
        return result.scalar()

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
