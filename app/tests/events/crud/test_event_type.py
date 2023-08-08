from sqlalchemy.orm import Session

from app.events import crud, models, schemas


class TestEventType:
    name = "event type name"
    slug = "event-type-slug"

    def test_create_event_type(self, db: Session) -> None:
        event_type_in = schemas.EventTypeCreate(name=self.name, slug=self.slug)
        event_type = crud.event_type.create(db, obj_in=event_type_in)
        assert event_type.name == self.name
        assert event_type.slug == self.slug

    def test_create_event_type_with_parent_type(self, db: Session, event_type: models.EventType) -> None:
        event_type_in = schemas.EventTypeCreate(name=self.name, slug=self.slug, parent_type_id=event_type.id)
        event_type2 = crud.event_type.create(db, obj_in=event_type_in)
        assert event_type2.parent_type_id == event_type.id
        assert len(event_type.children) == 1
        assert event_type.children[0].id == event_type2.id
        assert event_type2.parent is not None
        assert event_type2.parent.id == event_type.id

    def test_remove_event_type(self, db: Session, event_type: models.EventType) -> None:
        crud.event_type.remove(db, id_=event_type.id)
        event_type3 = crud.event_type.get(db, id_=event_type.id)
        assert event_type3 is None
