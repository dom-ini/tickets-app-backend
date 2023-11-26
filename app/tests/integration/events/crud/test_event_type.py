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

    def test_get_category_tree(self, db: Session, event_type: models.EventType) -> None:
        event_type_in = schemas.EventTypeCreate(name=self.name, slug=self.slug, parent_type_id=event_type.id)
        event_type2 = crud.event_type.create(db, obj_in=event_type_in)
        event_type_tree = crud.event_type.get_event_type_tree(db)
        assert event_type_tree
        assert event_type_tree[0].children[0].id == event_type2.id

    def test_get_parent_hierarchy(
        self, db: Session, event_type: models.EventType, nested_event_type: models.EventType
    ) -> None:
        result = crud.event_type.get_event_type_parent_hierarchy(db, event_type_id=nested_event_type.id)
        result_ids = [category[0] for category in result]
        expected_ids = [nested_event_type.id, event_type.id]
        assert result_ids == expected_ids

    def test_get_by_slug(self, db: Session, event_type: models.EventType) -> None:
        event_type2 = crud.event_type.get_by_slug(db, slug=event_type.slug)
        assert event_type2 is not None
        assert event_type2.id == event_type.id

    def test_remove_event_type(self, db: Session, event_type: models.EventType) -> None:
        crud.event_type.remove(db, id_=event_type.id)
        event_type3 = crud.event_type.get(db, id_=event_type.id)
        assert event_type3 is None
