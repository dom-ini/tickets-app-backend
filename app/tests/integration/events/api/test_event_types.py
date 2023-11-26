import pytest
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

    def test_get_event_type_by_slug(self, client: TestClient, event_type: models.EventType) -> None:
        r = client.get(f"{settings.API_V1_STR}/event-types/{event_type.slug}")
        result = r.json()
        assert r.status_code == status.HTTP_200_OK
        assert result.get("slug") == event_type.slug

    @pytest.mark.parametrize("test_hierarchy", [(False,), (True,)])
    def test_get_event_type_by_wrong_slug_should_fail(self, client: TestClient, test_hierarchy: bool) -> None:
        event_type_slug = "wrong-slug"
        url = f"{settings.API_V1_STR}/event-types/{event_type_slug}"
        if test_hierarchy:
            url += "/hierarchy"
        r = client.get(url)
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_get_event_type_hierarchy_by_slug(
        self, client: TestClient, event_type: models.EventType, nested_event_type: models.EventType
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/event-types/{nested_event_type.slug}/hierarchy")
        result = r.json()

        result_names = [item.get("name") for item in result]
        expected_names = [nested_event_type.name, event_type.name]

        assert result_names == expected_names
