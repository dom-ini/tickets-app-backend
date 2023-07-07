from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from starlette import status

from app.auth import crud, schemas
from app.auth.emails import send_password_reset_request_mail
from app.common import schemas as common_schemas
from app.common.deps import DBSession

router = APIRouter()


@router.post("/password/reset", response_model=common_schemas.MessageResponse)
def request_password_reset(
    db: DBSession,
    password_reset_request: schemas.PasswordResetRequest,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Request email message with password reset token
    """
    user = crud.user.get_by_email(db, email=password_reset_request.email)
    if user:
        crud.password_reset_token.invalidate_all(db)
        token_in = schemas.PasswordResetTokenCreate(user_id=user.id)
        token = crud.password_reset_token.generate(db, obj_in=token_in)
        background_tasks.add_task(send_password_reset_request_mail, email_to=user.email, token=token.value)
    return common_schemas.MessageResponse(
        message="If the given email address exists in the database, you will receive an email message with instruction "
        "how to reset your password"
    )


@router.post("/password/reset/confirm", response_model=common_schemas.MessageResponse)
def reset_password(db: DBSession, password_reset_form: schemas.PasswordResetForm) -> Any:
    """
    Reset password using the obtained token

    Password rules:
    * min. 8 characters long
    * min. 1 uppercase letter
    * min. 1 lowercase letter
    * min. 1 digit
    * min. 1 special character
    """
    token = crud.password_reset_token.get_by_value(db, value=password_reset_form.token)
    if not token or crud.password_reset_token.is_invalidated(token) or crud.password_reset_token.is_expired(token):
        raise HTTPException(detail="Invalid token", status_code=status.HTTP_400_BAD_REQUEST)
    crud.password_reset_token.invalidate(db, token=token)
    user_id = token.user_id
    user = crud.user.get(db, id_=user_id)
    if not user:
        raise HTTPException(detail="User not found", status_code=status.HTTP_400_BAD_REQUEST)
    crud.user.change_password(db, user=user, new_password=password_reset_form.new_password)
    return common_schemas.MessageResponse(message="Password changed successfully")
