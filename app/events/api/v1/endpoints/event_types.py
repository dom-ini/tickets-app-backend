from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.common.deps import DBSession
from app.events import crud, schemas
from app.events.deps import event_type_exists

router = APIRouter()


@router.get("/", response_model=list[schemas.EventTypeNode])
def list_event_types(db: DBSession) -> Any:
    """
    List event types
    """
    event_types = crud.event_type.get_event_type_tree(db)
    return event_types


@router.get("/{slug}", response_model=schemas.EventType)
def get_event_type_by_slug(event_type: Annotated[schemas.EventType, Depends(event_type_exists.by_slug)]) -> Any:
    """
    Read event type by slug
    """
    return event_type

