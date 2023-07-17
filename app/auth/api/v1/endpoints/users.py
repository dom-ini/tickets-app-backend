from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends
from starlette import status

from app.auth import crud, schemas
from app.auth.deps import open_registration_allowed, user_create_unique_email, user_update_unique_email, valid_user_id
from app.auth.emails import send_new_user_email
from app.common.deps import CurrentActiveUser, DBSession, Mailer, Pagination, get_current_active_superuser

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(open_registration_allowed)],
)
def create_user_open(
    db: DBSession,
    background_tasks: BackgroundTasks,
    registration_form: Annotated[schemas.UserCreate, Depends(user_create_unique_email)],
    mailer: Mailer,
) -> Any:
    """
    Open registration for unauthenticated users

    Password rules:
    * min. 8 characters long
    * min. 1 uppercase letter
    * min. 1 lowercase letter
    * min. 1 digit
    * min. 1 special character
    """
    user_in = schemas.UserCreate(email=registration_form.email, password=registration_form.password, is_activated=True)
    new_user = crud.user.create(db, obj_in=user_in)
    background_tasks.add_task(mailer.send, send_new_user_email(email_to=new_user.email))
    return new_user


@router.get("/", response_model=list[schemas.User], dependencies=[Depends(get_current_active_superuser)])
def list_users(db: DBSession, pagination: Pagination) -> Any:
    """
    List all users (for superusers only)
    """
    users = crud.user.get_all(db, limit=pagination.limit, skip=pagination.skip)
    return users


@router.get("/{user_id}", response_model=schemas.User, dependencies=[Depends(get_current_active_superuser)])
def read_user(user: Annotated[schemas.User, Depends(valid_user_id)]) -> Any:
    """
    Read user by id (for superusers only)
    """
    return user


@router.get("/me", response_model=schemas.User)
def read_current_user(user: CurrentActiveUser) -> Any:
    """
    Get currently authenticated user
    """
    return user


@router.patch("/me", response_model=schemas.User)
def update_current_user(
    db: DBSession, user: CurrentActiveUser, user_in: Annotated[schemas.UserUpdate, Depends(user_update_unique_email)]
) -> Any:
    """
    Update currently authenticated user
    """
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
