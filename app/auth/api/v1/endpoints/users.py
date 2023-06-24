from typing import Any

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException
from pydantic import EmailStr
from starlette import status

from app.auth import crud, schemas
from app.auth.utils import send_new_user_email
from app.common.deps import DBSession
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=schemas.User)
def create_user_open(
    db: DBSession,
    background_tasks: BackgroundTasks,
    email: EmailStr = Body(...),
    password: str = Body(..., regex=settings.PASSWORD_REGEX),
) -> Any:
    """
    Open registration for unauthenticated users
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(detail="Open registration is forbidden", status_code=status.HTTP_403_FORBIDDEN)
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(detail="Email already taken", status_code=status.HTTP_400_BAD_REQUEST)
    user_in = schemas.UserCreate(email=email, password=password, is_activated=True)
    new_user = crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED:
        background_tasks.add_task(send_new_user_email, email_to=new_user.email)
    return new_user
