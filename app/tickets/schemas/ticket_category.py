from pydantic import BaseModel, ConfigDict


class TicketCategoryBase(BaseModel):
    name: str
    quota: int


class TicketCategoryInDBBase(TicketCategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TicketCategory(TicketCategoryInDBBase):
    pass


class TicketCategoryCreate(TicketCategoryBase):
    event_id: int
