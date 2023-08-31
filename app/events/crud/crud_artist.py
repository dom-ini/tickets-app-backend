from app.common.crud import CRUDBase, SlugMixin
from app.common.schemas import EmptySchema
from app.events.models import Artist
from app.events.schemas import ArtistCreate


class CRUDArtist(CRUDBase[Artist, ArtistCreate, EmptySchema], SlugMixin[Artist]):
    pass
