from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import VerificationToken
from app.auth.schemas.verification_token import VerificationTokenCreate
from app.common.crud import CRUDBase, generate_unique_token
from app.common.schemas import EmptySchema


class CRUDVerificationToken(CRUDBase[VerificationToken, VerificationTokenCreate, EmptySchema]):
    def get_by_value(self, db: Session, *, value: str) -> VerificationToken | None:
        query = select(self.model).where(self.model.value == value)
        result = db.execute(query)
        return result.scalar()

    def create(self, db: Session, *, obj_in: VerificationTokenCreate) -> VerificationToken:
        token = generate_unique_token(db, token_model=self.model, payload={"user_id": obj_in.user_id})
        db.refresh(token)
        return token
