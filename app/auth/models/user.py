from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_activated = Column(Boolean(), default=False)
    is_disabled = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)
    joined_at = Column(DateTime, nullable=False, default=datetime.now)
