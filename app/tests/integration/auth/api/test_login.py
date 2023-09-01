import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import crud, models, schemas
from app.auth.utils import generate_valid_password
from app.core.config import settings


class TestLogin:
    password = generate_valid_password()

    @pytest.fixture(name="default_user")
    def create_default_user(self, db: Session) -> models.User:
        user_in = schemas.UserCreate(email="default@example.com", password=self.password, is_activated=True)
        return crud.user.create(db, obj_in=user_in)

    @pytest.fixture(name="inactive_user")
    def create_inactive_user(self, db: Session) -> models.User:
        user_in = schemas.UserCreate(email="inactive@example.com", password=self.password, is_activated=False)
        return crud.user.create(db, obj_in=user_in)

    @pytest.fixture(name="disabled_user")
    def create_disabled_user(self, db: Session) -> models.User:
        user_in = schemas.UserCreate(
            email="disabled@example.com", password=self.password, is_activated=True, is_disabled=True
        )
        return crud.user.create(db, obj_in=user_in)

    def test_get_access_token(self, client: TestClient, default_user: models.User) -> None:
        login_data = {
            "username": default_user.email,
            "password": self.password,
        }
        r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
        tokens = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert "access_token" in tokens
        assert tokens["access_token"]

    def test_disabled_user(self, client: TestClient, disabled_user: models.User) -> None:
        login_data = {
            "username": disabled_user.email,
            "password": self.password,
        }
        r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_inactive_user(self, client: TestClient, inactive_user: models.User) -> None:
        login_data = {
            "username": inactive_user.email,
            "password": self.password,
        }
        r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_get_access_token_invalid_credentials(self, client: TestClient) -> None:
        login_data = {
            "username": settings.TEST_USER_EMAIL,
            "password": "invalid_password",
        }
        r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_use_access_token(self, client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
        r = client.get(f"{settings.API_V1_STR}/auth/test-token", headers=normal_user_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert "email" in result
