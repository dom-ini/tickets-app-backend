from pydantic import BaseModel, HttpUrl


class ArtistBase(BaseModel):
    name: str
    photo: HttpUrl | None = None
    description: str
    slug: str


class ArtistInDBBase(ArtistBase):
    id: int

    class Config:
        orm_mode = True


class Artist(ArtistInDBBase):
    pass


class ArtistCreate(ArtistBase):
    pass
