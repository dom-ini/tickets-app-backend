from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.auth import schemas
from app.auth.deps import authenticate_and_authorize_user
from app.common import deps

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(access_token: Annotated[str, Depends(authenticate_and_authorize_user)]) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/test-token", response_model=schemas.User)
def test_token(current_user: deps.CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user
