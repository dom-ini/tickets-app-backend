from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.auth import crud, schemas, security
from app.common import deps
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(db: deps.DBSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate_by_mail(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not crud.user.is_activated(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not activated",
        )
    if crud.user.is_disabled(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
    )

    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/test-token", response_model=schemas.User)
def test_token(current_user: deps.CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user
