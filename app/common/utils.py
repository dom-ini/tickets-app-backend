from typing import Annotated, Generic, TypeVar

from fastapi import Path

from app.common.crud import CRUDBase, Model
from app.common.deps import DBSession

CRUD = TypeVar("CRUD", bound=CRUDBase)


class InstanceInDBValidator(Generic[Model, CRUD]):
    def __init__(self, crud_service: CRUD, exception: Exception) -> None:
        self.crud_service = crud_service
        self.exception = exception

    def instance_or_404(self, instance: Model | None) -> Model:
        if not instance:
            raise self.exception
        return instance

    def by_id(self, db: DBSession, id_: Annotated[int, Path(default=..., alias="id")]) -> Model:
        instance = self.crud_service.get(db, id_=id_)
        return self.instance_or_404(instance)
