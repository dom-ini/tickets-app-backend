from typing import Any

from fastapi import APIRouter

from app.common.deps import DBSession
from app.events import crud, schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.EventTypeNode])
def list_event_types(db: DBSession) -> Any:
    """
    List event types
    """
    event_types = crud.event_type.get_event_type_tree(db)
    return event_types
