from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.events import models


class TestSpeakers:
    def test_get_speaker_by_id(self, client: TestClient, speaker: models.Speaker) -> None:
        r = client.get(f"{settings.API_V1_STR}/speakers/{speaker.id}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("id") == speaker.id

    def test_get_speaker_by_wrong_id_should_fail(self, client: TestClient) -> None:
        speaker_id = 9999
        r = client.get(f"{settings.API_V1_STR}/speakers/{speaker_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND
