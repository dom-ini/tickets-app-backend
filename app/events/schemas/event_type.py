from pydantic import BaseModel


class EventTypeBase(BaseModel):
    name: str
    slug: str


class EventTypeInDBBase(EventTypeBase):
    id: int

    class Config:
        orm_mode = True


class EventType(EventTypeInDBBase):
    pass


class EventTypeCreate(EventTypeBase):
    parent_type_id: int | None = None
