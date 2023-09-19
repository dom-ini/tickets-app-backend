from app.auth.models import User
from app.tickets.models import Ticket, TicketCategory


def test_str_ticket(user_instance: User) -> None:
    ticket_id = 99
    payload = {
        "id": ticket_id,
        "email": "email@example.com",
        "token": "token",
        "user_id": 1,
        "ticket_category_id": 1,
    }
    ticket = Ticket(**payload)
    ticket.user = user_instance
    assert str(user_instance) in str(ticket) and str(ticket_id) in str(ticket)


def test_str_ticket_category() -> None:
    payload = {
        "name": "category-name",
        "quota": 100,
        "event_id": 1,
    }
    category = TicketCategory(**payload)
    assert str(payload.get("name")) in str(category) and str(payload.get("quota")) in str(category)
