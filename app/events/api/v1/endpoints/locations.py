from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.events import schemas
from app.events.deps import location_exists

router = APIRouter()


@router.get("/{slug}", response_model=schemas.Location)
def get_location_by_slug(location: Annotated[schemas.Location, Depends(location_exists.by_slug)]) -> Any:
    """
    Read location by slug
    """
    return location
