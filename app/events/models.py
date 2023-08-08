from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, relationship  # type: ignore

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.auth.models import User  # noqa: F401

event_artist = Table(
    "event_artist",
    Base.metadata,  # pylint: disable=E1101
    Column("event_id", ForeignKey("event.id"), primary_key=True),
    Column("artist_id", ForeignKey("artist.id"), primary_key=True),
)


class Event(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    poster_vertical = Column(String)
    poster_horizontal = Column(String)
    held_at = Column(DateTime, nullable=False)
    organizer_id = Column(Integer, ForeignKey("organizer.id"))
    created_by_id = Column(Integer, ForeignKey("user.id"))
    event_type_id = Column(Integer, ForeignKey("eventtype.id"))
    location_id = Column(Integer, ForeignKey("location.id"))

    organizer = relationship("Organizer", back_populates="events")
    created_by = relationship("User", back_populates="events")
    event_type = relationship("EventType", back_populates="events")
    location = relationship("Location", back_populates="events")
    artists: Mapped[list["Artist"]] = relationship(
        "Artist", secondary=event_artist, primaryjoin=(event_artist.c.event_id == id), back_populates="events"
    )


class Organizer(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True, index=True)

    events = relationship("Event", back_populates="organizer")


class EventType(Base):
    id = Column(Integer, primary_key=True, index=True)
    parent_type_id = Column(Integer, ForeignKey("eventtype.id"))
    name = Column(String(80), index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)

    parent = relationship("EventType", remote_side=[id], back_populates="children")
    children: Mapped[list["EventType"]] = relationship(
        "EventType", remote_side=[parent_type_id], back_populates="parent"
    )
    events = relationship("Event", back_populates="event_type", lazy="dynamic")


class Location(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), index=True, nullable=False)
    city = Column(String(40), index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)

    events = relationship("Event", back_populates="location", lazy="dynamic")


class Artist(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(40), index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    photo = Column(String)
    description = Column(Text)

    events = relationship(
        "Event", secondary=event_artist, secondaryjoin=(event_artist.c.artist_id == id), back_populates="artists"
    )
