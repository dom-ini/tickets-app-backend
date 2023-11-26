from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.common.deps import DBSession, Pagination
from app.common.schemas import Paginated
from app.common.utils import paginate
from app.events import crud, schemas
from app.events.deps import event_exists
from app.events.filters import EventFilters, EventSorter

router = APIRouter()


@router.get("/", response_model=Paginated[schemas.EventBrief])
def list_events(
    db: DBSession,
    pagination: Pagination,
    event_filter: Annotated[EventFilters, Depends()],
    event_sorter: Annotated[EventSorter, Depends()],
    only_with_available_tickets: bool = False,
) -> Any:
    """
    List events
    """
    filters = event_filter.filters
    events = crud.event.get_filtered(
        db,
        filters=filters.statements,
        joins=filters.related,
        only_with_available_tickets=only_with_available_tickets,
        order_by=event_sorter.order_by,
        limit=pagination.limit,
        skip=pagination.skip,
    )
    events_count = crud.event.get_filtered_count(
        db, filters=filters.statements, joins=filters.related, only_with_available_tickets=only_with_available_tickets
    )
    return paginate(events, events_count)


@router.get("/{slug}", response_model=schemas.EventDetails)
def get_event_by_slug(event: Annotated[schemas.EventDetails, Depends(event_exists.by_slug)]) -> Any:
    """
    Read event by slug
    """
    return event
