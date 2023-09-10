import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import crud
from app.auth.models import User, VerificationToken
from app.auth.schemas import VerificationTokenCreate
from app.core.config import settings


@pytest.fixture(name="verification_token")
def get_verification_token(db: Session, test_user: User) -> VerificationToken:
    token_in = VerificationTokenCreate(user_id=test_user.id)
    token = crud.verification_token.create(db, obj_in=token_in)
    return token


def test_verify_account_activates_account(
    client: TestClient, verification_token: VerificationToken, test_user: User
) -> None:
    r = client.post(f"{settings.API_V1_STR}/auth/verify/{verification_token.value}")
    assert r.status_code == status.HTTP_200_OK
    assert crud.user.is_activated(test_user)


def test_verify_account_with_invalid_token(client: TestClient) -> None:
    token = "invalid"
    r = client.post(f"{settings.API_V1_STR}/auth/verify/{token}")
    assert r.status_code == status.HTTP_400_BAD_REQUEST
