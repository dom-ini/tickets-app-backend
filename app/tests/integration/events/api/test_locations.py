from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.events import models


class TestLocations:
    def test_get_location_by_slug(self, client: TestClient, location: models.Location) -> None:
        r = client.get(f"{settings.API_V1_STR}/locations/{location.slug}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("slug") == location.slug

    def test_get_location_by_wrong_slug_should_fail(self, client: TestClient) -> None:
        event_slug = "wrong-slug"
        r = client.get(f"{settings.API_V1_STR}/locations/{event_slug}")
        assert r.status_code == status.HTTP_404_NOT_FOUND
