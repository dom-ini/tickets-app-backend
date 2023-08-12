from sqlalchemy.orm import Session

from app.events import crud, models, schemas


class TestArtist:
    def test_create_artist(self, db: Session) -> None:
        name = "artist"
        description = "description"
        slug = "artist-slug"
        photo = "https://example.com/"
        artist_in = schemas.ArtistCreate(name=name, description=description, slug=slug, photo=photo)
        artist = crud.artist.create(db, obj_in=artist_in)
        assert artist.name == name
        assert artist.description == description
        assert artist.slug == slug
        assert artist.photo == photo

    def test_get_by_slug(self, db: Session, artist: models.Artist) -> None:
        artist2 = crud.artist.get_by_slug(db, slug=artist.slug)
        assert artist2 is not None
        assert artist2.id == artist.id

    def test_remove_artist(self, db: Session, artist: models.Artist) -> None:
        crud.artist.remove(db, id_=artist.id)
        artist3 = crud.artist.get(db, id_=artist.id)
        assert artist3 is None
