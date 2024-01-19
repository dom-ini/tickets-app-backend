from datetime import date

from app.common.filters import BaseFilter, BaseSorter
from app.events.models import Event


class EventFilters(BaseFilter):
    name__icontains: str | None = None
    held_at__gte: date | None = None
    held_at__lte: date | None = None
    slug__exact: str | None = None
    is_active__exact: bool | None = None
    event_type_id__exact: int | None = None
    location_id__exact: int | None = None
    speakers__id__exact: int | None = None
    location__name__icontains: str | None = None
    location__city__icontains: str | None = None

    class Constants:
        model = Event


class EventSorter(BaseSorter):
    class Constants:
        model = Event
        order_by_fields = ["held_at", "name", "id"]
