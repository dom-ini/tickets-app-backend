# pylint: disable=no-self-argument
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.auth.utils import generate_valid_password, validate_password


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetForm(BaseModel):
    token: str
    new_password: str = Field(..., examples=[generate_valid_password()])

    @field_validator("new_password")
    def validate_new_password(cls, password: str) -> str:
        return validate_password(password)


class PasswordResetTokenBase(BaseModel):
    user_id: int


class PasswordResetTokenCreate(PasswordResetTokenBase):
    pass
