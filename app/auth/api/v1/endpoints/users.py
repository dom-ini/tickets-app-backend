from typing import Annotated, Any

from fastapi import APIRouter, Depends, status

from app.auth import crud, models, schemas
from app.auth.deps import (
    open_registration_allowed,
    register_new_user_and_send_verification_email,
    user_exists,
    user_update_unique_email,
)
from app.auth.exceptions import InvalidCurrentPassword
from app.common.deps import CurrentActiveUser, DBSession, Pagination, get_current_active_superuser

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(open_registration_allowed)],
)
def create_user_open(new_user: Annotated[models.User, Depends(register_new_user_and_send_verification_email)]) -> Any:
    """
    Open registration for unauthenticated users

    Password rules:
    * min. 8 characters long
    * min. 1 uppercase letter
    * min. 1 lowercase letter
    * min. 1 digit
    * min. 1 special character
    """
    return new_user


@router.get("/", response_model=list[schemas.User], dependencies=[Depends(get_current_active_superuser)])
def list_users(db: DBSession, pagination: Pagination) -> Any:
    """
    List all users (for superusers only)
    """
    users = crud.user.get_all(db, limit=pagination.limit, skip=pagination.skip)
    return users


@router.get("/me", response_model=schemas.User)
def read_current_user(user: CurrentActiveUser) -> Any:
    """
    Get currently authenticated user
    """
    return user


@router.patch("/me", response_model=schemas.User)
def update_current_user(
    db: DBSession,
    user: CurrentActiveUser,
    user_in: Annotated[schemas.UserUpdateWithCurrentPassword, Depends(user_update_unique_email)],
) -> Any:
    """
    Update currently authenticated user
    """
    if not crud.user.check_password(db, user=user, password=user_in.current_password):
        raise InvalidCurrentPassword
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.get("/{id}", response_model=schemas.User, dependencies=[Depends(get_current_active_superuser)])
def read_user(user: Annotated[schemas.User, Depends(user_exists.by_id)]) -> Any:
    """
    Read user by id (for superusers only)
    """
    return user
