# pylint: disable=W0212
from unittest.mock import Mock, call

import pytest
from fastapi.responses import RedirectResponse
from pytest_mock import MockerFixture
from sqladmin import ModelView

from app.admin_panel.views import EventView
from app.admin_panel.views.registry import register_view


@pytest.fixture(name="event_view")
def get_event_view() -> ModelView:
    return EventView()


@pytest.fixture(name="mock_update_model")
def get_mock_update_model(event_view: EventView, mocker: MockerFixture) -> Mock:
    mocked = mocker.patch.object(event_view, "update_model")
    return mocked


def test_register_view(mocker: MockerFixture) -> None:
    list_mock: list[Mock] = []
    mocker.patch("app.admin_panel.views.registry.admin_views", list_mock)
    view_mock = Mock()
    register_view(view_mock)

    assert list_mock[0] == view_mock


@pytest.mark.asyncio
async def test_event_insert_model_add_created_by_id_automatically(
    mocker: MockerFixture, event_view: EventView, mock_request: Mock
) -> None:
    user_id = 99
    mock_request.state.user.id = user_id
    payload = {"attribute": "value"}
    mocked = mocker.patch("app.admin_panel.views.events.ModelView.insert_model")
    await event_view.insert_model(request=mock_request, data=payload)

    mocked.assert_called_with(request=mock_request, data={**payload, "created_by_id": user_id})


@pytest.mark.asyncio
async def test_event_change_status_redirects_to_events_list(event_view: EventView, mock_request: Mock) -> None:
    mock_request.query_params.get.return_value = ""
    result = await event_view._change_status(request=mock_request, is_active=True)
    assert isinstance(result, RedirectResponse)
    assert "event/list" in result.headers.get("location", "")


@pytest.mark.asyncio
async def test_event_change_status_does_not_update_model_when_no_pks_are_given(
    event_view: EventView, mock_request: Mock, mock_update_model: Mock
) -> None:
    mock_request.query_params.get.return_value = ""
    await event_view._change_status(request=mock_request, is_active=True)

    mock_update_model.assert_not_called()


@pytest.mark.asyncio
async def test_event_change_status_updates_models_with_given_pk(
    event_view: EventView, mock_request: Mock, mock_update_model: Mock
) -> None:
    is_active = False
    pks = "1,2,3"
    mock_request.query_params.get.return_value = pks
    await event_view._change_status(request=mock_request, is_active=is_active)

    calls = [call(mock_request, pk=key, data={"is_active": is_active}) for key in pks.split(",")]
    mock_update_model.assert_has_calls(calls)
