from pydantic import BaseModel, ConfigDict, HttpUrl


class ArtistBase(BaseModel):
    name: str
    photo: HttpUrl | None = None
    description: str
    slug: str


class ArtistInDBBase(ArtistBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class Artist(ArtistInDBBase):
    pass


class ArtistCreate(ArtistBase):
    pass
