import pytest
from sqlalchemy.orm import Session

from app.auth.models import User
from app.events.models import Event
from app.tickets import crud
from app.tickets.models import Ticket, TicketCategory
from app.tickets.schemas import TicketCategoryCreate, TicketCreate


class TestTicket:
    @pytest.fixture(name="ticket_category_second")
    def create_second_ticket_category_for_event(self, db: Session, event: Event) -> TicketCategory:
        category_in = TicketCategoryCreate(name="second", quota=100, event_id=event.id)
        return crud.ticket_category.create(db, obj_in=category_in)

    @pytest.fixture(name="ticket_second")
    def create_ticket_for_second_ticket_category(
        self, db: Session, ticket_category_second: TicketCategory, test_user: User
    ) -> Ticket:
        ticket_in = TicketCreate(
            email="email@example.com", user_id=test_user.id, ticket_category_id=ticket_category_second.id
        )
        return crud.ticket.create(db, obj_in=ticket_in)

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

    def test_get_count_for_ticket_category(self, db: Session, ticket: Ticket) -> None:
        result = crud.ticket.get_count_for_ticket_category(db, ticket_category_id=ticket.ticket_category_id)
        assert result == 1

    @pytest.mark.usefixtures("ticket_category_second")
    def test_get_by_category_and_user(  # pylint: disable=R0913
        self,
        db: Session,
        ticket_category: TicketCategory,
        ticket: Ticket,
        ticket_second: Ticket,
        test_user: User,
    ) -> None:
        tickets = crud.ticket.get_by_category_and_user(db, user_id=test_user.id, ticket_category_id=ticket_category.id)
        assert len(tickets) == 2
        assert ticket in tickets
        assert ticket_second in tickets

    @pytest.mark.usefixtures("ticket_category_second")
    def test_get_by_event_and_user(  # pylint: disable=R0913
        self,
        db: Session,
        ticket_category: TicketCategory,
        ticket: Ticket,
        ticket_second: Ticket,
        test_user: User,
    ) -> None:
        tickets = crud.ticket.get_by_event_and_user(db, user_id=test_user.id, event_id=ticket_category.event_id)
        assert len(tickets) == 2
        assert ticket in tickets
        assert ticket_second in tickets
