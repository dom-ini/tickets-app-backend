from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship  # type: ignore[attr-defined]

from app.common.models import BoolFalse, IntPk, UniqueIndexedStr
from app.db.base_class import Base
from app.events.models import Event


class User(Base):
    id: Mapped[IntPk]
    email: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    hashed_password: Mapped[str]
    is_activated: Mapped[BoolFalse]
    is_disabled: Mapped[BoolFalse]
    is_superuser: Mapped[BoolFalse]
    joined_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken", back_populates="user"
    )
    events: Mapped[list["Event"]] = relationship(Event, back_populates="created_by")


class PasswordResetToken(Base):
    id: Mapped[IntPk]
    value: Mapped[UniqueIndexedStr]
    is_invalidated: Mapped[BoolFalse]
    expires_at: Mapped[datetime]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="password_reset_tokens")
