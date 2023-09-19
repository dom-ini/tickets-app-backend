from sqladmin import ModelView

from app.admin_panel.views.registry import register_view
from app.auth.models import User


@register_view
class UserView(ModelView, model=User):  # type: ignore[call-arg]
    icon = "fa-solid fa-user"
    column_list = [User.id, User.email, User.is_activated, User.joined_at]
    column_sortable_list = [User.id, User.email, User.is_activated, User.joined_at]
    column_searchable_list = [User.email]
    form_excluded_columns = [
        User.password_reset_tokens,
        User.verification_token,
        User.tickets,
        User.is_superuser,
        User.hashed_password,
    ]
    column_details_exclude_list = [User.password_reset_tokens, User.verification_token, User.tickets]
    can_delete = False
