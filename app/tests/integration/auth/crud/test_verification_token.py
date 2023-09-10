import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.auth import crud, models, schemas


class TestPasswordReset:
    user_id: int = 1
    value: str

    @pytest.fixture(name="verification_token")
    def create_verification_token(self, db: Session) -> models.VerificationToken:
        token_in = schemas.VerificationTokenCreate(user_id=self.user_id)
        token = crud.verification_token.create(db, obj_in=token_in)
        self.value = token.value
        return token

    def test_generate_token(self, verification_token: models.VerificationToken) -> None:
        assert isinstance(verification_token, models.VerificationToken)
        assert verification_token.user_id == self.user_id

    def test_get_by_value(self, db: Session, verification_token: models.VerificationToken) -> None:
        token = crud.verification_token.get_by_value(db, value=self.value)
        assert isinstance(token, models.VerificationToken)
        assert jsonable_encoder(token) == jsonable_encoder(verification_token)

    def test_remove_token(self, db: Session, verification_token: models.VerificationToken) -> None:
        crud.verification_token.remove(db, id_=verification_token.id)
        assert crud.verification_token.get(db, id_=verification_token.id) is None
