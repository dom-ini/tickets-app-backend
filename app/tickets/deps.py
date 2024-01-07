from typing import Annotated

from fastapi import Depends

from app.common.deps import CurrentActiveUser, DBSession
from app.common.utils import InstanceInDBValidator
from app.events import crud as crud_events
from app.tickets import crud, schemas
from app.tickets.crud import CRUDTicket, CRUDTicketCategory
from app.tickets.exceptions import (
    NoMoreTicketsLeft,
    TicketAlreadyReserved,
    TicketCategoryNotFound,
    TicketNotFound,
    TicketReservationNotAvailableForEvent,
)
from app.tickets.models import Ticket, TicketCategory

ticket_category_exists = InstanceInDBValidator[TicketCategory, CRUDTicketCategory](
    crud_service=crud.ticket_category, exception=TicketCategoryNotFound()
)
ticket_exists = InstanceInDBValidator[Ticket, CRUDTicket](crud_service=crud.ticket, exception=TicketNotFound())


def ticket_belongs_to_user(
    user: CurrentActiveUser, ticket: Annotated[schemas.TicketWithUser, Depends(ticket_exists.by_id)]
) -> schemas.Ticket:
    if not ticket.user_id == user.id:
        raise TicketNotFound
    return ticket


def validate_ticket_category(db: DBSession, ticket_body: schemas.TicketCreateBody) -> TicketCategory:
    category = ticket_category_exists.by_id(db, id_=ticket_body.ticket_category_id)
    event = category.event
    if not crud_events.event.is_active(event) or crud_events.event.is_expired(event):
        raise TicketReservationNotAvailableForEvent
    return category


def validate_ticket_payload(
    db: DBSession, ticket_body: schemas.TicketCreateBody, user: CurrentActiveUser
) -> schemas.TicketCreateBody:
    ticket = crud.ticket.get_by_category_and_user(
        db, user_id=user.id, ticket_category_id=ticket_body.ticket_category_id
    )
    if ticket:
        raise TicketAlreadyReserved
    return ticket_body


def reserve_ticket_if_available(
    db: DBSession,
    category: Annotated[TicketCategory, Depends(validate_ticket_category)],
    ticket_data: Annotated[schemas.TicketCreateBody, Depends(validate_ticket_payload)],
    user: CurrentActiveUser,
) -> Ticket:
    ticket_in = schemas.TicketCreate(**ticket_data.model_dump(), user_id=user.id)
    ticket_count_for_category = crud.ticket.get_count_for_ticket_category(db, ticket_category_id=category.id)
    if ticket_count_for_category >= category.quota:
        raise NoMoreTicketsLeft
    ticket = crud.ticket.create(db, obj_in=ticket_in)
    return ticket
