from unittest.mock import Mock

from sqlalchemy.exc import IntegrityError

from app.auth import crud
from app.auth.schemas import VerificationTokenCreate


def test_create_should_rollback_on_integrity_error(mock_db: Mock) -> None:
    mock_db.commit.side_effect = [IntegrityError("IntegrityError raised", orig=BaseException(), params=None), None]
    obj_in = VerificationTokenCreate(user_id=1)

    crud.verification_token.create(mock_db, obj_in=obj_in)

    mock_db.rollback.assert_called_once()


def test_create_contains_user_id(mock_db: Mock) -> None:
    user_id = 123
    obj_in = VerificationTokenCreate(user_id=user_id)
    token = crud.verification_token.create(mock_db, obj_in=obj_in)

    assert token.user_id == user_id
