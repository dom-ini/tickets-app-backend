from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_activated = Column(Boolean(), default=False)
    is_disabled = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")


class PasswordResetToken(Base):
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, nullable=False)
    is_invalidated = Column(Boolean(), default=False)
    expires_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", back_populates="password_reset_tokens")
