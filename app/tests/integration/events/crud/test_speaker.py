from sqlalchemy.orm import Session

from app.events import crud, models, schemas


class TestSpeaker:
    def test_create(self, db: Session) -> None:
        name = "speaker"
        description = "description"
        slug = "speaker-slug"
        photo = "https://example.com/"
        speaker_in = schemas.SpeakerCreate(name=name, description=description, slug=slug, photo=photo)
        speaker = crud.speaker.create(db, obj_in=speaker_in)
        assert speaker.name == name
        assert speaker.description == description
        assert speaker.slug == slug
        assert speaker.photo == photo

    def test_get_by_slug(self, db: Session, speaker: models.Speaker) -> None:
        speaker2 = crud.speaker.get_by_slug(db, slug=speaker.slug)
        assert speaker2 is not None
        assert speaker2.id == speaker.id

    def test_remove(self, db: Session, speaker: models.Speaker) -> None:
        crud.speaker.remove(db, id_=speaker.id)
        speaker3 = crud.speaker.get(db, id_=speaker.id)
        assert speaker3 is None
