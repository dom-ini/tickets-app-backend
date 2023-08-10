from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.events import schemas
from app.events.deps import artist_exists

router = APIRouter()


@router.get("/{id}", response_model=schemas.Artist)
def get_artist(artist: Annotated[schemas.Artist, Depends(artist_exists.by_id)]) -> Any:
    """
    Read artist by id
    """
    return artist
