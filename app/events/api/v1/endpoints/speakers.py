from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.events import schemas
from app.events.deps import speaker_exists

router = APIRouter()


@router.get("/{slug}", response_model=schemas.Speaker)
def get_speaker_by_slug(speaker: Annotated[schemas.Speaker, Depends(speaker_exists.by_slug)]) -> Any:
    """
    Read speaker by slug
    """
    return speaker
