from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.schemas import UserCreate, UserUpdate
from app.auth.security import get_password_hash, verify_password
from app.common.crud import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> User | None:
        query = select(self.model).where(func.lower(self.model.email) == func.lower(email))
        result = db.execute(query)
        return result.scalar()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = self.model(
            email=obj_in.email.lower(),
            hashed_password=get_password_hash(obj_in.password),
            is_superuser=obj_in.is_superuser,
            is_activated=obj_in.is_activated,
            is_disabled=obj_in.is_disabled,
            joined_at=obj_in.joined_at,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        new_password = update_data.get("new_password")
        if new_password:
            hashed_password = get_password_hash(new_password)
            del update_data["new_password"]
            update_data["hashed_password"] = hashed_password
        if update_data.get("email"):
            update_data["email"] = update_data["email"].lower()
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def check_password(self, db: Session, *, user: User, password: str) -> bool:
        authenticated_user = self.authenticate_by_mail(db, email=user.email, password=password)
        return bool(authenticated_user)

    def change_password(self, db: Session, *, user: User, new_password: str) -> User:
        user_in = UserUpdate(new_password=new_password)
        return self.update(db, db_obj=user, obj_in=user_in)

    def _set_attribute(self, db: Session, *, user_id: int, attr: str, value: Any) -> User | None:
        user = self.get(db, user_id)
        if not user:
            return None

        setattr(user, attr, value)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def deactivate(self, db: Session, *, user_id: int) -> User | None:
        user = self._set_attribute(db, user_id=user_id, attr="is_disabled", value=True)
        return user

    def activate(self, db: Session, *, user_id: int) -> User | None:
        user = self._set_attribute(db, user_id=user_id, attr="is_activated", value=True)
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
