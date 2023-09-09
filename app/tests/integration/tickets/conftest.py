import pytest
from sqlalchemy.orm import Session

from app.auth.models import User
from app.events.models import Event
from app.tickets import crud
from app.tickets.models import Ticket, TicketCategory
from app.tickets.schemas import TicketCategoryCreate, TicketCreate


@pytest.fixture(name="ticket_category")
def get_ticket_category(db: Session, event: Event) -> TicketCategory:
    category_in = TicketCategoryCreate(name="example", quota=100, event_id=event.id)
    return crud.ticket_category.create(db, obj_in=category_in)


@pytest.fixture(name="ticket")
def get_ticket(db: Session, ticket_category: TicketCategory, test_user: User) -> Ticket:
    ticket_in = TicketCreate(email="email@example.com", user_id=test_user.id, ticket_category_id=ticket_category.id)
    return crud.ticket.create(db, obj_in=ticket_in)


@pytest.fixture(name="ticket_categories")
def get_ticket_categories(db: Session, event: Event) -> list[TicketCategory]:
    categories = []
    for i in range(2):
        category_in = TicketCategoryCreate(name=f"category{i}", quota=100, event_id=event.id)
        category = crud.ticket_category.create(db, obj_in=category_in)
        categories.append(category)
    return categories


@pytest.fixture(name="user_tickets")
def get_user_tickets(db: Session, ticket_categories: list[TicketCategory], test_user: User) -> list[Ticket]:
    tickets = []
    for category in ticket_categories:
        ticket_in = TicketCreate(email="email@example.com", user_id=test_user.id, ticket_category_id=category.id)
        ticket = crud.ticket.create(db, obj_in=ticket_in)
        tickets.append(ticket)
    return tickets
