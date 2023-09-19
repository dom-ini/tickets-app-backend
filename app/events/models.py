from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship  # type: ignore[attr-defined]

from app.common.models import IntPk, UniqueIndexedStr
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.auth.models import User  # noqa: F401
    from app.tickets.models import TicketCategory  # noqa: F401

event_speaker = Table(
    "event_speaker",
    Base.metadata,
    Column("event_id", ForeignKey("event.id"), primary_key=True),
    Column("speaker_id", ForeignKey("speaker.id"), primary_key=True),
)


class Event(Base):
    id: Mapped[IntPk]
    name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    slug: Mapped[UniqueIndexedStr]
    description: Mapped[Optional[str]] = mapped_column(Text)
    poster_vertical: Mapped[Optional[str]]
    poster_horizontal: Mapped[Optional[str]]
    held_at: Mapped[datetime]
    organizer_id: Mapped[int] = mapped_column(ForeignKey("organizer.id"), nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    event_type_id: Mapped[int] = mapped_column(ForeignKey("eventtype.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), nullable=False)

    organizer: Mapped["Organizer"] = relationship("Organizer", back_populates="events")
    created_by: Mapped["User"] = relationship("User")
    event_type: Mapped["EventType"] = relationship("EventType", back_populates="events")
    location: Mapped["Location"] = relationship("Location", back_populates="events")
    speakers: Mapped[list["Speaker"]] = relationship("Speaker", secondary=event_speaker, back_populates="events")
    ticket_categories: Mapped[list["TicketCategory"]] = relationship("TicketCategory", back_populates="event")

    def __str__(self) -> str:
        return f"{self.name} ({self.held_at})"


class Organizer(Base):
    id: Mapped[IntPk]
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)

    events: Mapped[list["Event"]] = relationship("Event", back_populates="organizer")

    def __str__(self) -> str:
        return self.name


class EventType(Base):
    id: Mapped[IntPk]
    parent_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("eventtype.id"))
    name: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    slug: Mapped[UniqueIndexedStr]

    parent: Mapped[Optional["EventType"]] = relationship(
        "EventType", remote_side="EventType.id", back_populates="children"
    )
    children: Mapped[list["EventType"]] = relationship(
        "EventType", remote_side=[parent_type_id], back_populates="parent"
    )
    events: Mapped[list["Event"]] = relationship("Event", back_populates="event_type", lazy="dynamic")

    def __str__(self) -> str:
        return self.name


class Location(Base):
    id: Mapped[IntPk]
    name: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    city: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    slug: Mapped[UniqueIndexedStr]
    longitude: Mapped[float]
    latitude: Mapped[float]

    events: Mapped[list["Event"]] = relationship("Event", back_populates="location", lazy="dynamic")

    def __str__(self) -> str:
        return f"{self.name}, {self.city}"


class Speaker(Base):
    id: Mapped[IntPk]
    name: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    slug: Mapped[UniqueIndexedStr]
    photo: Mapped[Optional[str]]
    description: Mapped[Optional[str]] = mapped_column(Text)

    events: Mapped[list["Event"]] = relationship("Event", secondary=event_speaker, back_populates="speakers")

    def __str__(self) -> str:
        return self.name
