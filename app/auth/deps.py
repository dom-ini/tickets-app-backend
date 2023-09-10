from typing import Annotated

from fastapi import BackgroundTasks, Depends

from app.auth import crud, models, schemas
from app.auth.crud import CRUDUser
from app.auth.emails import send_new_user_email
from app.auth.exceptions import EmailAlreadyTaken, InvalidToken, OpenRegistrationNotAllowed, UserNotFound
from app.common.deps import CurrentActiveUser, DBSession, Mailer
from app.common.utils import InstanceInDBValidator
from app.core.config import settings

user_exists = InstanceInDBValidator[models.User, CRUDUser](crud_service=crud.user, exception=UserNotFound())


def validate_unique_email(db: DBSession, email: str) -> None:
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise EmailAlreadyTaken


def user_update_unique_email(
    db: DBSession, current_user: CurrentActiveUser, user_in: schemas.UserUpdate
) -> schemas.UserUpdate:
    if user_in.email is not None and not current_user.email == user_in.email:
        validate_unique_email(db, email=str(user_in.email))
    return user_in


def user_create_unique_email(db: DBSession, user_in: schemas.UserCreateOpen) -> schemas.UserCreateOpen:
    validate_unique_email(db, email=str(user_in.email))
    return user_in


def open_registration_allowed() -> None:
    if not settings.USERS_OPEN_REGISTRATION:
        raise OpenRegistrationNotAllowed


def register_user(
    db: DBSession, registration_form: Annotated[schemas.UserCreate, Depends(user_create_unique_email)]
) -> models.User:
    user_in = schemas.UserCreate(email=registration_form.email, password=registration_form.password)
    new_user = crud.user.create(db, obj_in=user_in)
    return new_user


def create_verification_token(
    db: DBSession, user: Annotated[models.User, Depends(register_user)]
) -> models.VerificationToken:
    token_in = schemas.VerificationTokenCreate(user_id=user.id)
    verification_token = crud.verification_token.create(db, obj_in=token_in)
    return verification_token


def register_new_user_and_send_verification_email(
    user: Annotated[models.User, Depends(register_user)],
    token: Annotated[models.VerificationToken, Depends(create_verification_token)],
    background_tasks: BackgroundTasks,
    mailer: Mailer,
) -> models.User:
    background_tasks.add_task(mailer.send, send_new_user_email(email_to=user.email, verification_token=token.value))
    return user


def verify_account(db: DBSession, token: str) -> None:
    token_instance = crud.verification_token.get_by_value(db, value=token)
    if not token_instance:
        raise InvalidToken
    crud.user.activate(db, user_id=token_instance.user_id)
    crud.verification_token.remove(db, id_=token_instance.id)
