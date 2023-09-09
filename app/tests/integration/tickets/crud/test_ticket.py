from sqlalchemy.orm import Session

from app.auth.models import User
from app.tickets import crud
from app.tickets.models import Ticket, TicketCategory
from app.tickets.schemas import TicketCreate


class TestTicket:
    def test_create(self, db: Session, test_user: User, ticket_category: TicketCategory) -> None:
        ticket_in = TicketCreate(email="email@example.com", user_id=test_user.id, ticket_category_id=ticket_category.id)
        ticket = crud.ticket.create(db, obj_in=ticket_in)
        assert isinstance(ticket, Ticket)
        assert ticket.email == ticket_in.email
        assert ticket.ticket_category_id == ticket_in.ticket_category_id
        assert ticket.user_id == ticket_in.user_id

    def test_get_by_token(self, db: Session, ticket: Ticket) -> None:
        ticket_by_token = crud.ticket.get_by_token(db, token=ticket.token)
        assert ticket_by_token == ticket

    def test_get_all_by_user(self, db: Session, user_tickets: list[Ticket], test_user: User) -> None:
        tickets = crud.ticket.get_all_by_user(db, user_id=test_user.id)
        assert len(tickets) == len(user_tickets)

    def test_get_by_ticket_category_and_user(self, db: Session, ticket: Ticket) -> None:
        result = crud.ticket.get_by_ticket_category_and_user(
            db, ticket_category_id=ticket.ticket_category_id, user_id=ticket.user_id
        )
        assert result == ticket

    def test_get_count_for_ticket_category(self, db: Session, ticket: Ticket) -> None:
        result = crud.ticket.get_count_for_ticket_category(db, ticket_category_id=ticket.ticket_category_id)
        assert result == 1
