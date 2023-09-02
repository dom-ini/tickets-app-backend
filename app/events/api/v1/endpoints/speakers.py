from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.events import schemas
from app.events.deps import speaker_exists

router = APIRouter()


@router.get("/{id}", response_model=schemas.Speaker)
def get_speaker(speaker: Annotated[schemas.Speaker, Depends(speaker_exists.by_id)]) -> Any:
    """
    Read speaker by id
    """
    return speaker
