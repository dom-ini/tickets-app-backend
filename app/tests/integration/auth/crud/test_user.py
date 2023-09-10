from datetime import datetime

import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.auth import crud, models, schemas
from app.auth.utils import generate_valid_password
from app.tests.integration.test_db_config.initial_data import INITIAL_DATA


class TestUser:  # pylint: disable=R0904
    email: str = "RaNdOm@eMaIl.com"
    password: str = generate_valid_password()
    joined_at: datetime = datetime.utcnow()

    @pytest.fixture(name="default_user")
    def create_default_user(self, db: Session) -> models.User:
        user_in = schemas.UserCreate(email=self.email, password=self.password, joined_at=self.joined_at)
        return crud.user.create(db, obj_in=user_in)

    @pytest.fixture(name="activated_superuser")
    def create_activated_superuser(self, db: Session) -> models.User:
        email = "1" + self.email
        user_in = schemas.UserCreate(
            email=email, password=self.password, is_activated=True, is_disabled=False, is_superuser=True
        )
        return crud.user.create(db, obj_in=user_in)

    @pytest.fixture(name="disabled_not_activated_user")
    def create_disabled_not_activated_user(self, db: Session) -> models.User:
        email = "2" + self.email
        user_in = schemas.UserCreate(
            email=email, password=self.password, is_activated=False, is_disabled=True, is_superuser=False
        )
        return crud.user.create(db, obj_in=user_in)

    def test_create_user_should_return_user_type(self, default_user: models.User) -> None:
        assert isinstance(default_user, models.User)

    def test_create_user_email_should_be_saved_lowercase(self, default_user: models.User) -> None:
        assert default_user.email == self.email.lower()

    def test_create_user_password_should_be_saved_as_hash(self, default_user: models.User) -> None:
        assert hasattr(default_user, "hashed_password")
        assert default_user.hashed_password != self.password

    def test_create_user_joined_at_should_be_saved_correctly(self, default_user: models.User) -> None:
        assert isinstance(default_user.joined_at, datetime)
        assert default_user.joined_at == self.joined_at

    def test_create_user_is_superuser_should_be_false_as_default(self, default_user: models.User) -> None:
        assert not crud.user.is_superuser(default_user)

    def test_create_user_is_activated_should_be_false_as_default(self, default_user: models.User) -> None:
        assert not crud.user.is_activated(default_user)

    def test_create_user_is_disabled_should_be_false_as_default(self, default_user: models.User) -> None:
        assert not crud.user.is_disabled(default_user)

    def test_is_activated_on_activated_user(self, activated_superuser: models.User) -> None:
        assert crud.user.is_activated(activated_superuser)

    def test_is_activated_on_not_activated_user(self, disabled_not_activated_user: models.User) -> None:
        assert not crud.user.is_activated(disabled_not_activated_user)

    def test_is_disabled_on_disabled_user(self, disabled_not_activated_user: models.User) -> None:
        assert crud.user.is_disabled(disabled_not_activated_user)

    def test_is_disabled_on_not_disabled_user(self, activated_superuser: models.User) -> None:
        assert not crud.user.is_disabled(activated_superuser)

    def test_is_superuser_on_superuser(self, activated_superuser: models.User) -> None:
        assert crud.user.is_superuser(activated_superuser)

    def test_is_superuser_on_not_superuser(self, disabled_not_activated_user: models.User) -> None:
        assert not crud.user.is_superuser(disabled_not_activated_user)

    def test_get_user_by_id(self, db: Session, default_user: models.User) -> None:
        user = crud.user.get(db, id_=default_user.id)
        assert isinstance(user, models.User)
        assert jsonable_encoder(user) == jsonable_encoder(default_user)

    def test_get_user_with_wrong_id_should_return_none(self, db: Session) -> None:
        user_id = 9999
        user = crud.user.get(db, id_=user_id)
        assert user is None

    def test_get_user_by_email(self, db: Session, default_user: models.User) -> None:
        user = crud.user.get_by_email(db, email=default_user.email)
        assert isinstance(user, models.User)
        assert jsonable_encoder(user) == jsonable_encoder(default_user)

    def test_get_user_by_wrong_email_should_return_none(self, db: Session) -> None:
        email = "wrong@email.com"
        user = crud.user.get_by_email(db, email=email)
        assert user is None

    def test_get_all_users_should_return_every_user(self, db: Session) -> None:
        users = crud.user.get_all(db)
        assert len(users) == len(INITIAL_DATA["users"].data)

    def test_authenticate_by_email_with_correct_credentials(self, db: Session, default_user: models.User) -> None:
        user = crud.user.authenticate_by_mail(db, email=self.email, password=self.password)
        assert isinstance(user, models.User)
        assert user.id == default_user.id

    def test_authenticate_by_email_with_incorrect_credentials_should_return_none(self, db: Session) -> None:
        email = "not_correct_email"
        password = "not_correct_password"
        user = crud.user.authenticate_by_mail(db, email=email, password=password)
        assert user is None

    def test_authenticate_by_email_with_incorrect_email_should_return_none(
        self, db: Session, default_user: models.User
    ) -> None:
        email = default_user.email + "incorrect"
        password = self.password
        user = crud.user.authenticate_by_mail(db, email=email, password=password)
        assert user is None

    def test_authenticate_by_email_with_incorrect_password_should_return_none(
        self, db: Session, default_user: models.User
    ) -> None:
        email = default_user.email
        password = "not_correct_password"
        user = crud.user.authenticate_by_mail(db, email=email, password=password)
        assert user is None

    def test_activate_user(self, db: Session, default_user: models.User) -> None:
        crud.user.activate(db, user_id=default_user.id)
        assert crud.user.is_activated(default_user)

    def test_activate_user_with_wrong_id_should_return_none(self, db: Session) -> None:
        user_id = 9999
        user = crud.user.activate(db, user_id=user_id)
        assert user is None

    def test_deactivate_user(self, db: Session, default_user: models.User) -> None:
        crud.user.deactivate(db, user_id=default_user.id)
        assert crud.user.is_disabled(default_user)

    def test_deactivate_user_with_wrong_id_should_return_none(self, db: Session) -> None:
        user_id = 9999
        user = crud.user.deactivate(db, user_id=user_id)
        assert user is None

    def test_updated_user_should_have_new_values(self, db: Session, default_user: models.User) -> None:
        new_email = "new_random@email.com"
        user_in = schemas.UserUpdate(email=new_email)
        crud.user.update(db, db_obj=default_user, obj_in=user_in)
        assert default_user.email == new_email

    def test_updated_user_email_should_be_saved_lowercase(self, db: Session, default_user: models.User) -> None:
        new_email = "nEw_raNDom@eMaIl.cOm"
        user_in = schemas.UserUpdate(email=new_email)
        crud.user.update(db, db_obj=default_user, obj_in=user_in)
        assert default_user.email == new_email.lower()

    def test_updated_user_should_not_overwrite_unset_values(self, db: Session, default_user: models.User) -> None:
        new_password = generate_valid_password()
        old_email = default_user.email
        user_in = schemas.UserUpdate(password=new_password)
        crud.user.update(db, db_obj=default_user, obj_in=user_in)
        assert default_user.email == old_email

    def test_updated_user_password_should_be_saved_as_hash(self, db: Session, default_user: models.User) -> None:
        new_password = generate_valid_password()
        user_in = schemas.UserUpdate(password=new_password)
        crud.user.update(db, db_obj=default_user, obj_in=user_in)
        assert default_user.hashed_password != new_password

    def test_update_user_dict_payload(self, db: Session, default_user: models.User) -> None:
        new_email = "new@email.com"
        user_in = {"email": new_email}
        crud.user.update(db, db_obj=default_user, obj_in=user_in)
        assert default_user.email == new_email

    def test_change_password(self, db: Session, default_user: models.User) -> None:
        new_password = generate_valid_password()
        old_password_hash = default_user.hashed_password
        crud.user.change_password(db, user=default_user, new_password=new_password)
        assert old_password_hash != default_user.hashed_password
