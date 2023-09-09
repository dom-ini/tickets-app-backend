from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class TicketBase(BaseModel):
    email: EmailStr


class TicketInDBBase(TicketBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class Ticket(TicketInDBBase):
    token: str
    created_at: datetime


class TicketWithUser(Ticket):
    user_id: int


class TicketCreateBody(TicketBase):
    ticket_category_id: int


class TicketCreate(TicketCreateBody):
    user_id: int
