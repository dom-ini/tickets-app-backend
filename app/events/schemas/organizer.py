from pydantic import BaseModel


class OrganizerBase(BaseModel):
    name: str


class OrganizerInDBBase(OrganizerBase):
    id: int

    class Config:
        orm_mode = True


class Organizer(OrganizerInDBBase):
    pass


class OrganizerCreate(OrganizerBase):
    pass
