from typing import Annotated

from fastapi import BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import crud, models, schemas, security
from app.auth.crud import CRUDUser
from app.auth.emails import send_new_user_email, send_password_reset_request_mail
from app.auth.exceptions import (
    EmailAlreadyTaken,
    InvalidCredentials,
    InvalidToken,
    OpenRegistrationNotAllowed,
    UserDisabled,
    UserNotActivated,
    UserNotFound,
)
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


def authenticate_and_authorize_user(db: DBSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> str:
    user = crud.user.authenticate_by_mail(db, email=form_data.username, password=form_data.password)
    if not user:
        raise InvalidCredentials
    if not crud.user.is_activated(user):
        raise UserNotActivated
    if crud.user.is_disabled(user):
        raise UserDisabled

    access_token = security.create_access_token(subject=user.id)
    return access_token


def process_reset_password_request(
    db: DBSession,
    password_reset_request: schemas.PasswordResetRequest,
    background_tasks: BackgroundTasks,
    mailer: Mailer,
) -> None:
    user = crud.user.get_by_email(db, email=password_reset_request.email)
    if user is None:
        return
    crud.password_reset_token.invalidate_all(db, user_id=user.id)
    token_in = schemas.PasswordResetTokenCreate(user_id=user.id)
    token = crud.password_reset_token.create(db, obj_in=token_in)
    background_tasks.add_task(mailer.send, send_password_reset_request_mail(email_to=user.email, token=token.value))


def invalidate_password_reset_token(
    db: DBSession, password_reset_form: schemas.PasswordResetForm
) -> models.PasswordResetToken:
    token = crud.password_reset_token.get_by_value(db, value=password_reset_form.token)
    if not token or crud.password_reset_token.is_invalidated(token) or crud.password_reset_token.is_expired(token):
        raise InvalidToken
    crud.password_reset_token.invalidate(db, token=token)
    return token


def reset_user_password(
    db: DBSession,
    password_reset_form: schemas.PasswordResetForm,
    token: Annotated[models.PasswordResetToken, Depends(invalidate_password_reset_token)],
) -> None:
    user = user_exists.by_id(db, id_=token.user_id)
    crud.user.change_password(db, user=user, new_password=password_reset_form.new_password)
