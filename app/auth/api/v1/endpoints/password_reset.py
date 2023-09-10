from typing import Any

from fastapi import APIRouter, Depends

from app.auth.deps import process_reset_password_request, reset_user_password
from app.common import schemas as common_schemas

router = APIRouter()


@router.post(
    "/password/reset",
    response_model=common_schemas.MessageResponse,
    dependencies=[Depends(process_reset_password_request)],
)
def request_password_reset() -> Any:
    """
    Request email message with password reset token
    """
    return common_schemas.MessageResponse(
        message="If the given email address exists in the database, you will receive an email message with instruction "
        "how to reset your password"
    )


@router.post(
    "/password/reset/confirm",
    response_model=common_schemas.MessageResponse,
    dependencies=[Depends(reset_user_password)],
)
def reset_password() -> Any:
    """
    Reset password using the obtained token

    Password rules:
    * min. 8 characters long
    * min. 1 uppercase letter
    * min. 1 lowercase letter
    * min. 1 digit
    * min. 1 special character
    """
    return common_schemas.MessageResponse(message="Password changed successfully")
