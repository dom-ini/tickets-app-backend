from datetime import datetime

from sqlalchemy.orm import Session

from app.common.crud import CRUDBase, FilterableMixin, SlugMixin
from app.common.schemas import EmptySchema
from app.events.models import Event, Speaker
from app.events.schemas import EventCreate


class CRUDEvent(CRUDBase[Event, EventCreate, EmptySchema], SlugMixin[Event], FilterableMixin[Event]):
    def speakers(self, event: Event) -> list[Speaker]:
        return event.speakers

    def add_speaker(self, db: Session, *, event: Event, speaker: Speaker) -> None:
        event.speakers.append(speaker)
        db.commit()

    def remove_speaker(self, db: Session, *, event: Event, speaker: Speaker) -> None:
        event.speakers.remove(speaker)
        db.commit()

    def is_active(self, event: Event) -> bool:
        return event.is_active

    def is_expired(self, event: Event) -> bool:
        return datetime.utcnow() > event.held_at
