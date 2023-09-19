from sqladmin import ModelView

from app.tickets.models import Ticket, TicketCategory

from .registry import register_view


@register_view
class TicketView(ModelView, model=Ticket):  # type: ignore[call-arg]
    icon = "fa-solid fa-ticket"
    column_list = [Ticket.id, Ticket.email, Ticket.ticket_category, Ticket.user]
    column_searchable_list = [Ticket.email]
    column_sortable_list = [Ticket.id, Ticket.email]
    column_details_exclude_list = [Ticket.user_id, Ticket.ticket_category_id]
    can_delete = False
    can_edit = False
    can_create = False


@register_view
class TicketCategoryView(ModelView, model=TicketCategory):  # type: ignore[call-arg]
    name_plural = "Ticket Categories"
    icon = "fa-solid fa-layer-group"
    column_list = [TicketCategory.id, TicketCategory.name, TicketCategory.quota, TicketCategory.event]
    column_searchable_list = [TicketCategory.name]
    column_sortable_list = [TicketCategory.id, TicketCategory.name, TicketCategory.quota]
    form_excluded_columns = [TicketCategory.tickets]
    column_details_exclude_list = [TicketCategory.event_id, TicketCategory.tickets]
    form_ajax_refs = {
        "event": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
    }
