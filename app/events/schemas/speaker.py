from pydantic import BaseModel, ConfigDict, HttpUrl


class SpeakerBase(BaseModel):
    name: str
    photo: HttpUrl | None = None
    description: str
    slug: str


class SpeakerInDBBase(SpeakerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class Speaker(SpeakerInDBBase):
    pass


class SpeakerCreate(SpeakerBase):
    pass
