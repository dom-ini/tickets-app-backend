from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.common.deps import DBSession, Pagination
from app.events import crud, schemas
from app.events.deps import event_exists

router = APIRouter()


@router.get("/", response_model=list[schemas.EventBrief])
def list_events(db: DBSession, pagination: Pagination) -> Any:
    """
    List events
    """
    events = crud.event.get_all(db, limit=pagination.limit, skip=pagination.skip)
    return events


@router.get("/{id}", response_model=schemas.EventDetails)
def get_event(event: Annotated[schemas.EventDetails, Depends(event_exists.by_id)]) -> Any:
    """
    Read event by id
    """
    return event
