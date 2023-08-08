# Import all the models, so that Base has them before being
# imported by Alembic
from app.auth.models import PasswordResetToken, User  # noqa pylint: disable=W0611
from app.db.base_class import Base  # noqa pylint: disable=W0611
from app.events.models import Artist, Event, EventType, Location, Organizer  # noqa pylint: disable=W0611
