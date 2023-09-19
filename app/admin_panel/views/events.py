from typing import Any

from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action

from app.events.models import Event, EventType, Location, Organizer, Speaker

from ...core.config import settings
from ..fields import CKTextAreaField
from .registry import register_view


@register_view
class EventView(ModelView, model=Event):  # type: ignore[call-arg]
    icon = "fa-solid fa-calendar-days"
    column_list = [Event.id, Event.name, Event.held_at, Event.is_active, Event.slug]
    column_searchable_list = [Event.name, Event.slug]
    column_sortable_list = [Event.id, Event.name, Event.held_at, Event.is_active, Event.slug]
    form_excluded_columns = [Event.ticket_categories, Event.speakers, Event.created_by]
    column_details_exclude_list = [Event.location_id, Event.organizer_id, Event.created_by_id, Event.event_type_id]
    form_ajax_refs = {
        "organizer": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
        "event_type": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
        "location": {
            "fields": ("name", "id", "city"),
            "order_by": "name",
        },
    }
    form_overrides = {
        "description": CKTextAreaField,
    }
    edit_template = "edit.html"
    create_template = "create.html"

    async def insert_model(self, request: Request, data: dict) -> Any:
        data["created_by_id"] = request.state.user.id
        return await super().insert_model(request=request, data=data)

    async def _change_status(self, request: Request, is_active: bool) -> RedirectResponse:
        primary_keys = request.query_params.get("pks", "")
        if primary_keys:
            for key in primary_keys.split(","):
                payload = {"is_active": is_active}
                await self.update_model(request, pk=key, data=payload)

        return RedirectResponse(f"{settings.ADMIN_PANEL_PATH}/event/list")

    @action(
        name="bulk_activate",
        label="Activate selected items",
        confirmation_message="Are you sure?",
        add_in_detail=False,
    )
    async def bulk_activate(self, request: Request) -> RedirectResponse:
        return await self._change_status(request, is_active=True)

    @action(
        name="bulk_deactivate",
        label="Deactivate selected items",
        confirmation_message="Are you sure?",
        add_in_detail=False,
    )
    async def bulk_deactivate(self, request: Request) -> RedirectResponse:
        return await self._change_status(request, is_active=False)


@register_view
class OrganizerView(ModelView, model=Organizer):  # type: ignore[call-arg]
    icon = "fa-solid fa-file-pen"
    column_list = [Organizer.id, Organizer.name]
    column_searchable_list = [Organizer.name]
    column_sortable_list = [Organizer.id, Organizer.name]
    form_excluded_columns = [Organizer.events]


@register_view
class EventTypeView(ModelView, model=EventType):  # type: ignore[call-arg]
    icon = "fa-solid fa-sitemap"
    column_list = [EventType.id, EventType.name, EventType.parent, EventType.slug]
    column_details_exclude_list = [EventType.events, EventType.parent_type_id]
    column_searchable_list = [EventType.name, EventType.slug]
    column_sortable_list = [EventType.id, EventType.name, EventType.slug]
    form_excluded_columns = [EventType.events, EventType.children]
    form_ajax_refs = {
        "parent": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
    }


@register_view
class LocationView(ModelView, model=Location):  # type: ignore[call-arg]
    icon = "fa-solid fa-location-dot"
    column_list = [Location.id, Location.name, Location.city, Location.slug]
    column_searchable_list = [Location.name, Location.city, Location.slug]
    column_sortable_list = [Location.id, Location.name, Location.city, Location.slug]
    form_excluded_columns = [Location.events]
    column_details_exclude_list = [Location.events]


@register_view
class SpeakerView(ModelView, model=Speaker):  # type: ignore[call-arg]
    icon = "fa-solid fa-chalkboard-user"
    column_list = [Speaker.id, Speaker.name, Speaker.slug]
    column_searchable_list = [Speaker.name, Speaker.slug]
    column_sortable_list = [Speaker.id, Speaker.name, Speaker.slug]
    form_excluded_columns = [Speaker.events]
    column_details_exclude_list = [Speaker.events]
    form_overrides = {"description": CKTextAreaField}
    edit_template = "edit.html"
    create_template = "create.html"
