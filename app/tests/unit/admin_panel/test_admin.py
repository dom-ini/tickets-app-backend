from unittest.mock import Mock, call

import pytest
from sqladmin import Admin

from app.admin_panel.admin import create_admin_app, register_views_in_admin_panel


@pytest.fixture(name="admin")
def get_admin() -> Mock:
    return Mock()


def test_register_views_in_admin_panel(admin: Mock) -> None:
    views_mock = [Mock(), Mock(), Mock()]
    register_views_in_admin_panel(admin=admin, views=views_mock)  # type: ignore[arg-type]
    calls = [call(view) for view in views_mock]

    admin.add_view.assert_has_calls(calls)


def test_register_views_in_admin_panel_with_empty_list(admin: Mock) -> None:
    register_views_in_admin_panel(admin=admin, views=[])

    admin.add_view.assert_not_called()


def test_create_admin_app_should_return_admin() -> None:
    auth_backend_mock = Mock()
    auth_backend_mock.middlewares = []
    result = create_admin_app(app=Mock(), engine=Mock(), auth_backend=auth_backend_mock)
    assert isinstance(result, Admin)
