import pytest
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.common.crud import CRUDBase, SlugMixin


class Model:
    id = 1
    slug = "slug"

    def __init__(self, **kwargs: dict) -> None:
        self.__dict__.update(kwargs)


class CreateSchema(BaseModel):
    pass


class UpdateSchema(BaseModel):
    pass


class SampleCRUD(CRUDBase[Model, CreateSchema, UpdateSchema], SlugMixin[Model]):  # type: ignore[type-var]
    def get_by_token(self, db: Session, token: str) -> Model | None:
        pass


@pytest.fixture(name="mock_crud", scope="session")
def get_mock_crud() -> SampleCRUD:
    return SampleCRUD(Model)
