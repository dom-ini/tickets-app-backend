from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship  # type: ignore[attr-defined]

from app.common.models import IntPk, UniqueIndexedStr
from app.db.base_class import Base
from app.events.models import Event

if TYPE_CHECKING:
    from app.auth.models import User  # noqa: F401


class Ticket(Base):
    id: Mapped[IntPk]
    email: Mapped[str] = mapped_column(index=True, nullable=False)
    token: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    ticket_category_id: Mapped[int] = mapped_column(ForeignKey("ticketcategory.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="tickets")
    ticket_category: Mapped["TicketCategory"] = relationship("TicketCategory", back_populates="tickets")


class TicketCategory(Base):
    id: Mapped[IntPk]
    name: Mapped[UniqueIndexedStr]
    quota: Mapped[int] = mapped_column(nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=False)

    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="ticket_category")
    event: Mapped["Event"] = relationship(Event, back_populates="ticket_categories")
