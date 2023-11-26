from sqlalchemy.orm import Session

from app.events import crud, models, schemas


class TestLocation:
    def test_create_location(self, db: Session) -> None:
        name = "location"
        city = "city"
        slug = "location-slug"
        latitude = 50.0
        longitude = 18.0
        location_in = schemas.LocationCreate(name=name, city=city, slug=slug, latitude=latitude, longitude=longitude)
        location = crud.location.create(db, obj_in=location_in)
        assert location.name == name
        assert location.city == city
        assert location.slug == slug
        assert location.latitude == latitude
        assert location.longitude == longitude

    def test_get_by_slug(self, db: Session, location: models.Location) -> None:
        location2 = crud.location.get_by_slug(db, slug=location.slug)
        assert location2 is not None
        assert location2.id == location.id

    def test_remove_location(self, db: Session, location: models.Location) -> None:
        crud.location.remove(db, id_=location.id)
        location3 = crud.location.get(db, id_=location.id)
        assert location3 is None
