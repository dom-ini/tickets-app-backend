from app.common.crud import CRUDBase, SlugMixin
from app.common.schemas import EmptySchema
from app.events.models import Location
from app.events.schemas import LocationCreate


class CRUDLocation(CRUDBase[Location, LocationCreate, EmptySchema], SlugMixin[Location]):
    pass
