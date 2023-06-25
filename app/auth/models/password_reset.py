from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.auth.models import User  # noqa


class PasswordResetToken(Base):
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, nullable=False)
    is_invalidated = Column(Boolean(), default=False)
    expires_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", back_populates="password_reset_tokens")
