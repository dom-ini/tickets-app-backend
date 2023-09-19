import asyncio
from typing import Any, Type
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from fastapi.responses import RedirectResponse
from pytest_mock import MockerFixture

from app.admin_panel.auth import TOKEN_SESSION_KEY, AdminAuth, RequestUser, _make_request, get_access_token, get_user


def mock_httpx_response(json_data: dict[str, Any], raise_error: bool = False) -> dict[str, Any]:
    mock_response = Mock()
    mock_response.json.return_value = json_data
    if raise_error:
        mock_response.raise_for_status.side_effect = httpx.RequestError("Error")
    return mock_response


@pytest.fixture(name="mock_make_request")
def get_mock_make_request(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch("app.admin_panel.auth._make_request")
    return mocked


@pytest.fixture(name="user_payload")
def get_user_payload() -> dict[str, Any]:
    return {"id": 1, "email": "email@example.com", "is_superuser": False}


@pytest.fixture(name="admin_auth")
def get_admin_auth() -> AdminAuth:
    return AdminAuth(secret_key="secret")


@pytest.fixture(name="request_with_form")
def get_request_mock_with_form(mock_request: Mock) -> Mock:
    form_return: asyncio.Future[dict[str, str]] = asyncio.Future()
    form_return.set_result({"username": "username", "password": "password"})
    mock_request.form.return_value = form_return
    return mock_request


@pytest.fixture(name="mock_get_user")
def get_mock_get_user(mocker: MockerFixture) -> Mock:
    mocked = mocker.patch("app.admin_panel.auth.get_user")
    return mocked


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "json_response,raise_error,expected",
    [
        ({"key": "value"}, False, {"key": "value"}),
        ({}, True, None),
    ],
)
async def test_make_request(
    mocker: MockerFixture, json_response: dict[str, Any], raise_error: bool, expected: Any
) -> None:
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    get_return: asyncio.Future[dict[str, Any]] = asyncio.Future()
    get_return.set_result(mock_httpx_response(json_response, raise_error=raise_error))
    mock_response.get.return_value = await get_return
    mock_client.__aenter__.return_value = mock_response
    mocker.patch("app.admin_panel.auth.httpx.AsyncClient", return_value=mock_client)
    result = await _make_request("/example", "get")

    assert result == expected


@pytest.mark.asyncio
async def test_get_access_token_returns_access_token(mock_make_request: Mock) -> None:
    access_token = "token"
    mock_make_request.return_value = {"access_token": access_token}
    result = await get_access_token({})

    assert result == access_token


@pytest.mark.asyncio
async def test_get_access_token_returns_none_if_no_response(mock_make_request: Mock) -> None:
    mock_make_request.return_value = None
    result = await get_access_token({})

    assert result is None


@pytest.mark.asyncio
async def test_get_user_returns_request_user(mock_make_request: Mock, user_payload: dict[str, Any]) -> None:
    mock_make_request.return_value = user_payload
    result = await get_user("token")

    assert isinstance(result, RequestUser)


@pytest.mark.asyncio
async def test_get_user_request_user_has_correct_attributes(
    mock_make_request: Mock, user_payload: dict[str, Any]
) -> None:
    mock_make_request.return_value = user_payload
    result = await get_user("token")

    assert all(getattr(result, key) == value for key, value in user_payload.items())


@pytest.mark.asyncio
async def test_get_user_returns_none_if_no_response(mock_make_request: Mock) -> None:
    mock_make_request.return_value = None
    result = await get_user("token")

    assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token_response,expected",
    [
        (None, False),
        ("token", True),
    ],
)
async def test_admin_auth_login(
    admin_auth: AdminAuth, request_with_form: Mock, token_response: str | None, expected: bool, mocker: MockerFixture
) -> None:
    mocker.patch("app.admin_panel.auth.get_access_token", return_value=token_response)
    result = await admin_auth.login(request_with_form)

    assert result == expected


@pytest.mark.asyncio
async def test_admin_auth_login_sets_token_in_session_if_successful(
    admin_auth: AdminAuth, request_with_form: Mock, mocker: MockerFixture
) -> None:
    token = "token"
    mocker.patch("app.admin_panel.auth.get_access_token", return_value=token)
    await admin_auth.login(request_with_form)

    request_with_form.session.update.assert_called_with({TOKEN_SESSION_KEY: token})


@pytest.mark.asyncio
async def test_admin_auth_logout_returns_true(admin_auth: AdminAuth, mock_request: Mock) -> None:
    result = await admin_auth.logout(mock_request)

    assert result


@pytest.mark.asyncio
async def test_admin_auth_logout_clears_session(admin_auth: AdminAuth, mock_request: Mock) -> None:
    await admin_auth.logout(mock_request)

    mock_request.session.clear.assert_called_once()


@pytest.mark.asyncio
async def test_admin_auth_authenticate_returns_redirect_if_no_token_in_session(
    admin_auth: AdminAuth, mock_request: Mock
) -> None:
    mock_request.session.get.return_value = None
    result = await admin_auth.authenticate(mock_request)

    assert isinstance(result, RedirectResponse)


@pytest.mark.asyncio
async def test_admin_auth_authenticate_sets_user_in_session(
    admin_auth: AdminAuth, mock_request: Mock, mock_get_user: Mock
) -> None:
    user = Mock()
    mock_get_user.return_value = user
    mock_request.session.get.return_value = "token"
    await admin_auth.authenticate(mock_request)

    assert mock_request.state.user == user


@pytest.mark.asyncio
async def test_admin_auth_authenticate_returns_redirect_if_no_response(
    admin_auth: AdminAuth, mock_request: Mock, mock_get_user: Mock
) -> None:
    mock_get_user.return_value = None
    mock_request.session.get.return_value = "token"
    result = await admin_auth.authenticate(mock_request)

    assert isinstance(result, RedirectResponse)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_superuser,expected_type", [(False, RedirectResponse), (True, type(None))])
async def test_admin_auth_authenticate_when_user_is_in_response(
    admin_auth: AdminAuth, mock_request: Mock, mock_get_user: Mock, is_superuser: bool, expected_type: Type
) -> None:
    user = Mock()
    user.is_superuser = is_superuser
    mock_get_user.return_value = user
    mock_request.session.get.return_value = "token"
    result = await admin_auth.authenticate(mock_request)

    assert isinstance(result, expected_type)
