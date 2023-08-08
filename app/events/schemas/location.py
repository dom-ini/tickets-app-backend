from pydantic import BaseModel, ConfigDict


class LocationBase(BaseModel):
    name: str
    city: str


class LocationInDBBase(LocationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


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
