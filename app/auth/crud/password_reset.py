import secrets
from datetime import datetime, timedelta

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.models.password_reset import PasswordResetToken
from app.auth.schemas import PasswordResetTokenCreate
from app.common.crud import CRUDBase
from app.core.config import settings


class CRUDPasswordResetToken(CRUDBase[PasswordResetToken, PasswordResetTokenCreate, BaseModel]):
    def get_by_value(self, db: Session, *, value: str) -> PasswordResetToken | None:
        return db.query(self.model).filter(self.model.value == value).first()

    def generate(self, db: Session, *, obj_in: PasswordResetTokenCreate) -> PasswordResetToken:
        while True:
            token_value = secrets.token_urlsafe(64)
            expires_at = datetime.utcnow() + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
            token = self.model(user_id=obj_in.user_id, value=token_value, expires_at=expires_at)
            db.add(token)
            try:
                db.commit()
                break
            except IntegrityError:
                db.rollback()
        return token

    def invalidate(self, db: Session, *, token: PasswordResetToken) -> PasswordResetToken:
        token.is_invalidated = True
        db.commit()
        db.refresh(token)
        return token

    def invalidate_all(self, db: Session) -> None:
        tokens = db.query(self.model).filter(self.model.is_invalidated.is_(False))
        tokens.update({self.model.is_invalidated: True})
        db.commit()

    def is_invalidated(self, token: PasswordResetToken) -> bool:
        return token.is_invalidated

    def is_expired(self, token: PasswordResetToken) -> bool:
        return datetime.utcnow() >= token.expires_at
