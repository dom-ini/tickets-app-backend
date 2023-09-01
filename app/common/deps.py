from typing import Annotated, Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.auth import crud, models, schemas
from app.auth.exceptions import InvalidCredentials, NotEnoughPermissions, UserDisabled, UserNotActivated, UserNotFound
from app.common.emails import MailSender, mailer
from app.core.config import settings
from app.db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
DEFAULT_PAGE_SIZE = 100
DEFAULT_PAGE_OFFSET = 0


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(db: "DBSession", token: Annotated[str, Depends(oauth2_scheme)]) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        token_data = schemas.TokenPayload(sub=payload["sub"])
    except (jwt.JWTError, ValidationError) as exc:
        raise InvalidCredentials from exc
    user = crud.user.get(db, id_=token_data.sub)
    if not user:
        raise UserNotFound
    return user


def get_current_active_user(current_user: "CurrentUser") -> models.User:
    if not crud.user.is_activated(current_user):
        raise UserNotActivated
    if crud.user.is_disabled(current_user):
        raise UserDisabled
    return current_user


def get_current_active_superuser(current_user: "CurrentActiveUser") -> models.User:
    if not crud.user.is_superuser(current_user):
        raise NotEnoughPermissions
    return current_user


class PaginationParams:
    def __init__(self, skip: int = DEFAULT_PAGE_OFFSET, limit: int = DEFAULT_PAGE_SIZE) -> None:
        self.skip = skip
        self.limit = limit


DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[models.User, Depends(get_current_user)]
CurrentActiveUser = Annotated[models.User, Depends(get_current_active_user)]
CurrentActiveSuperUser = Annotated[models.User, Depends(get_current_active_superuser)]
Pagination = Annotated[PaginationParams, Depends()]
Mailer = Annotated[MailSender, Depends(mailer)]
