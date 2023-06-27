# pylint: disable=no-self-argument
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, validator

from app.auth.utils import generate_valid_password, validate_password


class UserBase(BaseModel):
    email: EmailStr
    is_activated: bool | None = False
    is_disabled: bool | None = False
    is_superuser: bool | None = False
    joined_at: datetime | None = Field(default_factory=datetime.now)


class UserCreate(UserBase):
    password: str

    @validator("password")
    def validate_password(cls, password: str) -> str:
        return validate_password(password)


class UserCreateOpen(BaseModel):
    email: EmailStr
    password: str = Field(..., example=generate_valid_password())

    @validator("password")
    def validate_password(cls, password: str) -> str:
        return validate_password(password)


class UserUpdate(BaseModel):
    email: EmailStr | None = None  # type: ignore
    password: str | None = Field(None, example=generate_valid_password())

    @validator("password")
    def validate_password(cls, password: str | None) -> str | None:
        if password is None:
            return password
        return validate_password(password)


class UserInDBBase(UserBase):
    id: int

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
