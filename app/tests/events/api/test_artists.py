from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.events import models


class TestArtists:
    def test_get_artist_by_id(self, client: TestClient, artist: models.Artist) -> None:
        r = client.get(f"{settings.API_V1_STR}/artists/{artist.id}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("id") == artist.id

    def test_get_artist_by_wrong_id_should_fail(self, client: TestClient) -> None:
        artist_id = 9999
        r = client.get(f"{settings.API_V1_STR}/artists/{artist_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND
