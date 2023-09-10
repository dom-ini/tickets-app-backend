from typing import Any

from fastapi import APIRouter, Depends

from app.auth.deps import verify_account
from app.common.schemas import MessageResponse

router = APIRouter()


@router.post("/verify/{token}", response_model=MessageResponse, dependencies=[Depends(verify_account)])
def activate_account() -> Any:
    return MessageResponse(message="Account activated successfully")
