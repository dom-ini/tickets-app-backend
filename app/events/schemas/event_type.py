from pydantic import BaseModel, ConfigDict


class EventTypeBase(BaseModel):
    name: str
    slug: str


class EventTypeInDBBase(EventTypeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class EventType(EventTypeInDBBase):
    pass


class EventTypeNode(EventTypeInDBBase):
    children: list["EventTypeNode"] | None = None


class EventTypeCreate(EventTypeBase):
    parent_type_id: int | None = None
