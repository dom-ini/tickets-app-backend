# pylint: disable=W0611
# Import all the models, so that Base has them before being
# imported by Alembic
from app.auth.models import PasswordResetToken, User  # noqa
from app.db.base_class import Base  # noqa
from app.events.models import Event, EventType, Location, Organizer, Speaker, event_speaker  # noqa
from app.tickets.models import Ticket, TicketCategory  # noqa
