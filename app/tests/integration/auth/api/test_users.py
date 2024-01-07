from typing import Generator

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import crud, schemas
from app.auth.utils import generate_valid_password
from app.common.deps import Mailer
from app.core.config import settings
from app.tests.integration.test_db_config.initial_data import INITIAL_DATA


class TestUsers:  # pylint: disable=R0904
    password = generate_valid_password()
    created_users_count = 10

    @pytest.fixture(name="create_users")
    def create_users(self, db: Session) -> None:
        for i in range(self.created_users_count):
            user_in = schemas.UserCreate(email=f"{i}@example.com", password=self.password, is_activated=True)
            crud.user.create(db, obj_in=user_in)

    @pytest.fixture(name="disallow_open_registration")
    def override_open_registration(self) -> Generator:
        old_setting = settings.USERS_OPEN_REGISTRATION
        settings.USERS_OPEN_REGISTRATION = False
        yield
        settings.USERS_OPEN_REGISTRATION = old_setting

    @pytest.fixture(name="deactivate_user")
    def deactivate_test_user(self, db: Session) -> None:
        user = crud.user.get_by_email(db, email=settings.TEST_USER_EMAIL)
        if not user:
            raise LookupError("User not found")
        user.is_activated = False
        db.add(user)
        db.commit()

    @pytest.fixture(name="disable_user")
    def disable_test_user(self, db: Session) -> None:
        user = crud.user.get_by_email(db, email=settings.TEST_USER_EMAIL)
        if not user:
            raise LookupError("User not found")
        crud.user.deactivate(db, user_id=user.id)

    def test_create_user_open_user_is_not_activated(self, client: TestClient, mail_engine: Mailer) -> None:
        password = generate_valid_password()
        email = "random@email.com"
        payload = {"email": email, "password": password}
        with mail_engine.record_messages() as outbox:
            r = client.post(f"{settings.API_V1_STR}/users/", json=payload)
            assert len(outbox) == 1
        result = r.json()
        assert r.status_code == status.HTTP_201_CREATED
        assert "email" in result
        assert not result.get("is_activated")

    @pytest.mark.usefixtures("disallow_open_registration")
    def test_create_user_open_disallowed_open_registration_should_fail(self, client: TestClient) -> None:
        password = generate_valid_password()
        email = "random@email.com"
        payload = {"email": email, "password": password}
        r = client.post(f"{settings.API_V1_STR}/users/", json=payload)
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_create_user_open_weak_password_should_fail(self, client: TestClient) -> None:
        password = "weak"
        email = "random@email.com"
        payload = {"email": email, "password": password}
        r = client.post(f"{settings.API_V1_STR}/users/", json=payload)
        assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_users_by_normal_user_should_fail(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/users/", headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_list_users_by_unauthenticated_user_should_fail(self, client: TestClient) -> None:
        r = client.get(f"{settings.API_V1_STR}/users/")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_users_by_superuser(self, client: TestClient, superuser_token_headers: dict[str, str]) -> None:
        r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == len(INITIAL_DATA["users"].data)

    @pytest.mark.usefixtures("create_users")
    def test_list_users_pagination(self, client: TestClient, superuser_token_headers: dict[str, str]) -> None:
        limit = 5
        skip = len(INITIAL_DATA["users"].data)
        r = client.get(f"{settings.API_V1_STR}/users/?limit={limit}&skip={skip}", headers=superuser_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == limit
        assert result[0].get("email") not in [settings.TEST_USER_EMAIL, settings.TEST_SUPERUSER_EMAIL]

    def test_read_current_user_by_unauthenticated_user_should_fail(self, client: TestClient) -> None:
        r = client.get(f"{settings.API_V1_STR}/users/me")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_read_current_user_by_normal_user(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("email") == settings.TEST_USER_EMAIL
        assert not result.get("is_superuser")

    def test_read_current_user_by_not_activated_user_should_fail(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        deactivate_user: None,  # pylint: disable=W0613
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_read_current_user_by_disabled_user_should_fail(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        disable_user: None,  # pylint: disable=W0613
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_read_current_user_by_superuser(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("email") == settings.TEST_SUPERUSER_EMAIL
        assert result.get("is_superuser")

    def test_read_user_by_id(self, client: TestClient, superuser_token_headers: dict[str, str]) -> None:
        user_id = 1
        r = client.get(f"{settings.API_V1_STR}/users/{user_id}", headers=superuser_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("email") == INITIAL_DATA["users"].data[0].get("email")

    def test_read_user_by_id_by_normal_user_should_fail(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        user_id = 1
        r = client.get(f"{settings.API_V1_STR}/users/{user_id}", headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_read_user_by_id_by_unauthenticated_user_should_fail(self, client: TestClient) -> None:
        user_id = 1
        r = client.get(f"{settings.API_V1_STR}/users/{user_id}")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_read_user_by_id_wrong_id_should_fail(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        user_id = 9999
        r = client.get(f"{settings.API_V1_STR}/users/{user_id}", headers=superuser_token_headers)
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_update_current_user_by_unauthenticated_user_should_fail(self, client: TestClient) -> None:
        r = client.patch(f"{settings.API_V1_STR}/users/me")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_current_user_should_not_change_superuser_status(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        payload = {"is_superuser": True, "current_password": settings.TEST_USER_PASSWORD}
        r = client.patch(f"{settings.API_V1_STR}/users/me", json=payload, headers=normal_user_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert not result.get("is_superuser")

    def test_update_current_user_new_email(self, client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
        new_email = "new@example.com"
        payload = {"email": new_email, "current_password": settings.TEST_USER_PASSWORD}
        r = client.patch(f"{settings.API_V1_STR}/users/me", json=payload, headers=normal_user_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("email") == new_email

    def test_update_current_user_already_taken_email_should_fail(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        new_email = settings.TEST_SUPERUSER_EMAIL
        payload = {"email": new_email, "current_password": settings.TEST_USER_PASSWORD}
        r = client.patch(f"{settings.API_V1_STR}/users/me", json=payload, headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_current_user_new_password(
        self, db: Session, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        new_password = generate_valid_password()
        payload = {"new_password": new_password, "current_password": settings.TEST_USER_PASSWORD}
        r = client.patch(f"{settings.API_V1_STR}/users/me", json=payload, headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_200_OK
        assert crud.user.authenticate_by_mail(db, email=settings.TEST_USER_EMAIL, password=new_password)

    def test_update_current_user_weak_new_password_should_fail(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        new_password = "weak"
        payload = {"new_password": new_password, "current_password": settings.TEST_USER_PASSWORD}
        r = client.patch(f"{settings.API_V1_STR}/users/me", json=payload, headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_current_user_partial_update_should_not_overwrite_data(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        new_password = generate_valid_password()
        payload = {"new_password": new_password, "current_password": settings.TEST_USER_PASSWORD}
        r = client.patch(f"{settings.API_V1_STR}/users/me", json=payload, headers=normal_user_token_headers)
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("email") == settings.TEST_USER_EMAIL

    def test_update_current_user_invalid_password_should_fail(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        new_email = "new@example.com"
        payload = {"email": new_email, "current_password": "invalid"}
        r = client.patch(f"{settings.API_V1_STR}/users/me", json=payload, headers=normal_user_token_headers)
        assert r.status_code == status.HTTP_403_FORBIDDEN
