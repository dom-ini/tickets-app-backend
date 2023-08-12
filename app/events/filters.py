from datetime import date

from app.common.filters import BaseFilter
from app.events.models import Event


class EventFilters(BaseFilter):
    name__icontains: str | None = None
    held_at__gte: date | None = None
    held_at__lte: date | None = None
    slug__exact: str | None = None
    event_type_id__exact: int | None = None
    location_id__exact: int | None = None

    class Constants:
        model = Event
