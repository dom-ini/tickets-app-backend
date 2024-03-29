from typing import Annotated, Any

from fastapi import APIRouter, Depends, status

from app.common.deps import CurrentActiveUser, DBSession, Pagination, get_current_active_user
from app.tickets import crud, schemas
from app.tickets.deps import reserve_ticket_if_available, ticket_belongs_to_user, ticket_exists
from app.tickets.models import Ticket

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.Ticket,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
def reserve_ticket(reserved_ticket: Annotated[Ticket, Depends(reserve_ticket_if_available)]) -> Any:
    """
    Reserve ticket for event (max. 1 per user)
    """
    return reserved_ticket


@router.get("/", response_model=list[schemas.TicketWithEvent])
def get_tickets_by_user(
    db: DBSession, user: CurrentActiveUser, pagination: Pagination, event_id: int | None = None
) -> Any:
    """Get all tickets reserved by current user"""
    if event_id is not None:
        return crud.ticket.get_by_event_and_user(
            db, user_id=user.id, event_id=event_id, limit=pagination.limit, skip=pagination.skip
        )
    tickets = crud.ticket.get_all_by_user(db, user_id=user.id, limit=pagination.limit, skip=pagination.skip)
    return tickets


@router.get("/token/{token}", response_model=schemas.SafeTicketWithEvent)
def get_ticket_by_token(ticket: Annotated[schemas.SafeTicketWithEvent, Depends(ticket_exists.by_token)]) -> Any:
    """Get ticket by token"""
    return ticket


@router.get("/{id}", response_model=schemas.Ticket, dependencies=[Depends(get_current_active_user)])
def get_ticket(ticket: Annotated[schemas.Ticket, Depends(ticket_belongs_to_user)]) -> Any:
    """Get ticket by id (must belong to the user)"""
    return ticket


@router.delete("/{id}", response_model=schemas.Ticket, dependencies=[Depends(get_current_active_user)])
def resign_from_ticket(db: DBSession, ticket: Annotated[schemas.Ticket, Depends(ticket_belongs_to_user)]) -> Any:
    """Resign from ticket (must belong to the user)"""
    deleted_ticket = crud.ticket.remove(db, id_=ticket.id)
    return deleted_ticket
