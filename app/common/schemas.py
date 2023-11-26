from typing import Generic, TypeVar

from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)


class MessageResponse(BaseModel):
    message: str


class EmptySchema(BaseModel):
    pass


class Paginated(BaseModel, Generic[M]):
    items: list[M]
    total_count: int
