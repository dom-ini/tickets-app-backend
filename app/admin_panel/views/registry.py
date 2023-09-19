from typing import Type

from sqladmin import BaseView, ModelView

admin_views = []


def register_view(cls: Type[ModelView | BaseView]) -> Type[ModelView | BaseView]:
    admin_views.append(cls)
    return cls
