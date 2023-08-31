from sqlalchemy.orm import Session

from app.common.crud import CRUDBase, FilterableMixin, SlugMixin
from app.common.schemas import EmptySchema
from app.events.models import Artist, Event
from app.events.schemas import EventCreate


class CRUDEvent(CRUDBase[Event, EventCreate, EmptySchema], SlugMixin[Event], FilterableMixin[Event]):
    def artists(self, event: Event) -> list[Artist]:
        return event.artists

    def add_artist(self, db: Session, *, event: Event, artist: Artist) -> None:
        event.artists.append(artist)
        db.commit()

    def remove_artist(self, db: Session, *, event: Event, artist: Artist) -> None:
        event.artists.remove(artist)
        db.commit()
