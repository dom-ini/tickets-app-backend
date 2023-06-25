from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetForm(BaseModel):
    token: str
    new_password: str = Field(..., regex=settings.PASSWORD_REGEX)


class PasswordResetTokenBase(BaseModel):
    user_id: int


class PasswordResetTokenCreate(PasswordResetTokenBase):
    pass
