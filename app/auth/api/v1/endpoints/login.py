from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import crud, schemas, security
from app.auth.exceptions import InvalidCredentials, UserDisabled, UserNotActivated
from app.common import deps

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(db: deps.DBSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate_by_mail(db, email=form_data.username, password=form_data.password)
    if not user:
        raise InvalidCredentials
    if not crud.user.is_activated(user):
        raise UserNotActivated
    if crud.user.is_disabled(user):
        raise UserDisabled

    access_token = security.create_access_token(subject=user.id)

    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/test-token", response_model=schemas.User)
def test_token(current_user: deps.CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user
