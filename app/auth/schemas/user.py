from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.core.settings import settings


# shared properties
class UserBase(BaseModel):
    email: EmailStr
    is_activated: bool | None = False
    is_disabled: bool | None = False
    is_superuser: bool | None = False
    joined_at: datetime | None = Field(default_factory=datetime.now)


# additional properties on creation
class UserCreate(UserBase):
    password: str = Field(..., regex=settings.PASSWORD_REGEX)


# additional properties on update
class UserUpdate(UserBase):
    password: str | None = Field(default=None, regex=settings.PASSWORD_REGEX)
    email: EmailStr | None = None  # type: ignore


class UserInDBBase(UserBase):
    id: int

    class Config:
        orm_mode = True


# properties to return via API
class User(UserInDBBase):
    pass


# additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
