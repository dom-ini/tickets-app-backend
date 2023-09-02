from app.common.crud import CRUDBase, SlugMixin
from app.common.schemas import EmptySchema
from app.events.models import Speaker
from app.events.schemas import SpeakerCreate


class CRUDSpeaker(CRUDBase[Speaker, SpeakerCreate, EmptySchema], SlugMixin[Speaker]):
    pass
