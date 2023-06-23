from typing import Any, Dict, Union

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.models.user import User
from app.auth.schemas.user import UserCreate, UserUpdate
from app.auth.security import get_password_hash, verify_password
from app.common.crud import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> User | None:
        return db.query(self.model).filter(func.lower(self.model.email) == func.lower(email)).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = self.model(
            email=obj_in.email.lower(),
            hashed_password=get_password_hash(obj_in.password),
            is_superuser=obj_in.is_superuser,  # type: ignore
            is_activated=obj_in.is_activated,  # type: ignore
            joined_at=obj_in.joined_at,  # type: ignore
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(obj_in.password)  # type: ignore
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        if update_data.get("email"):
            update_data["email"] = update_data["email"].lower()
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def deactivate(self, db: Session, *, user_id: int) -> User | None:
        user = db.query(self.model).get(user_id)
        if not user:
            return None

        user.is_disabled = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate_by_mail(self, db: Session, *, email: str, password: str) -> User | None:
        user = self.get_by_email(db, email=email)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user

    def is_activated(self, user: User) -> bool:
        return user.is_activated

    def is_disabled(self, user: User) -> bool:
        return user.is_disabled

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser
