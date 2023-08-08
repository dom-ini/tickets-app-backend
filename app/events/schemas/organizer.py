from pydantic import BaseModel, ConfigDict


class OrganizerBase(BaseModel):
    name: str


class OrganizerInDBBase(OrganizerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class Organizer(OrganizerInDBBase):
    pass


class OrganizerCreate(OrganizerBase):
    pass
