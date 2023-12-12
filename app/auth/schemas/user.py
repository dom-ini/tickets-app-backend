# pylint: disable=no-self-argument
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.auth.utils import generate_valid_password, validate_password


class UserBase(BaseModel):
    email: EmailStr
    is_activated: bool = False
    is_disabled: bool = False
    is_superuser: bool = False
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        return validate_password(password)


class UserCreateOpen(BaseModel):
    email: EmailStr
    password: str = Field(..., examples=[generate_valid_password()])

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        return validate_password(password)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    new_password: str | None = Field(None, examples=[generate_valid_password()])

    @field_validator("new_password")
    def validate_password(cls, new_password: str | None) -> str | None:
        if new_password is None:
            return new_password
        return validate_password(new_password)


class UserUpdateWithCurrentPassword(UserUpdate):
    current_password: str


class UserInDBBase(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
