from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.events import schemas
from app.events.deps import valid_artist_id

router = APIRouter()


@router.get("/{artist_id}", response_model=schemas.Artist)
def get_artist(artist: Annotated[schemas.Artist, Depends(valid_artist_id)]) -> Any:
    """
    Read artist by id
    """
    return artist
