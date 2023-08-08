from pydantic import BaseModel


class LocationBase(BaseModel):
    name: str
    city: str


class LocationInDBBase(LocationBase):
    id: int

    class Config:
        orm_mode = True


class Location(LocationInDBBase):
    latitude: float
    longitude: float
    slug: str


class SimpleLocation(LocationInDBBase):
    pass


class LocationCreate(LocationBase):
    latitude: float
    longitude: float
    slug: str
