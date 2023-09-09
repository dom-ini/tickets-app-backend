from app.tickets.crud.crud_ticket import CRUDTicket
from app.tickets.crud.crud_ticket_category import CRUDTicketCategory
from app.tickets.models import Ticket, TicketCategory

ticket = CRUDTicket(Ticket)
ticket_category = CRUDTicketCategory(TicketCategory)
