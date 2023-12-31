from pydantic import BaseModel, ConfigDict


class TicketCategoryBase(BaseModel):
    name: str
    quota: int


class TicketCategoryInDBBase(TicketCategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TicketCategory(TicketCategoryInDBBase):
    pass


class _TicketCategoryEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    slug: str


class TicketCategoryWithEvent(TicketCategory):
    event: _TicketCategoryEvent


class TicketCategoryWithLeftCount(BaseModel):
    ticket_category: TicketCategory
    tickets_left: int


class TicketCategoryCreate(TicketCategoryBase):
    event_id: int
