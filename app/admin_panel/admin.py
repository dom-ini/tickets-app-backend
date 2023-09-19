from typing import Type

from fastapi import FastAPI
from sqladmin import Admin, BaseView, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import Engine  # type: ignore[attr-defined]

from app.admin_panel.auth import authentication_backend
from app.admin_panel.views import admin_views
from app.core.config import settings


def register_views_in_admin_panel(admin: Admin, views: list[Type[ModelView | BaseView]]) -> None:
    for view in views:
        admin.add_view(view)


def create_admin_app(app: FastAPI, engine: Engine, auth_backend: AuthenticationBackend) -> Admin:
    admin = Admin(
        app,
        engine,
        authentication_backend=auth_backend,
        templates_dir="app/admin_panel/templates",
        base_url=settings.ADMIN_PANEL_PATH,
    )
    return admin


def setup_admin(app: FastAPI, engine: Engine) -> None:
    admin = create_admin_app(app=app, engine=engine, auth_backend=authentication_backend)
    register_views_in_admin_panel(admin, views=admin_views)
