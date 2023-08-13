from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.events import models


class TestEventTypes:
    def test_list_event_types(self, client: TestClient, event_type: models.EventType) -> None:
        r = client.get(f"{settings.API_V1_STR}/event-types")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert len(result) == 1
        assert result[0].get("id") == event_type.id
        assert isinstance(result[0].get("children"), list)
