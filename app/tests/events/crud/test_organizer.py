from sqlalchemy.orm import Session

from app.events import crud, models, schemas


class TestOrganizer:
    def test_create_organizer(self, db: Session) -> None:
        name = "organizer"
        organizer_in = schemas.OrganizerCreate(name=name)
        organizer = crud.organizer.create(db, obj_in=organizer_in)
        assert organizer.name == name

    def test_remove_organizer(self, db: Session, organizer: models.Organizer) -> None:
        crud.organizer.remove(db, id_=organizer.id)
        organizer3 = crud.organizer.get(db, id_=organizer.id)
        assert organizer3 is None
