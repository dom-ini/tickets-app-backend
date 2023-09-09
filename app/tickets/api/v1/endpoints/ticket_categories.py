from typing import Any

from fastapi import APIRouter

from app.common.deps import DBSession, Pagination
from app.tickets import crud, schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.TicketCategory])
def get_ticket_categories_by_event(db: DBSession, event_id: int, pagination: Pagination) -> Any:
    categories = crud.ticket_category.get_all_by_event(
        db, event_id=event_id, limit=pagination.limit, skip=pagination.skip
    )
    return categories
