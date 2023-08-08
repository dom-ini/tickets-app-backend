from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class EmptySchema(BaseModel):
    pass
