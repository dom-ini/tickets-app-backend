from typing import Annotated, Any, Generic, Sequence, TypeVar, Union

from fastapi import Path

from app.common.crud import CRUDBase, Model, SlugMixin
from app.common.deps import DBSession

CRUD = TypeVar("CRUD", bound=Union[CRUDBase, SlugMixin])


class InstanceInDBValidator(Generic[Model, CRUD]):
    def __init__(self, crud_service: CRUD, exception: Exception) -> None:
        self.crud_service = crud_service
        self.exception = exception

    def instance_or_404(self, instance: Model | None) -> Model:
        if not instance:
            raise self.exception
        return instance

    def by_id(self, db: DBSession, id_: Annotated[int, Path(default=..., alias="id")]) -> Model:
        if not hasattr(self.crud_service, "get"):
            raise NotImplementedError("CRUD service does not implement retrieving by id")
        instance = self.crud_service.get(db, id_=id_)
        return self.instance_or_404(instance)

    def by_slug(self, db: DBSession, slug: str) -> Model:
        if not hasattr(self.crud_service, "get_by_slug"):
            raise NotImplementedError("CRUD service does not implement retrieving by slug")
        instance = self.crud_service.get_by_slug(db, slug=slug)
        return self.instance_or_404(instance)


def paginate(items: Sequence, count: int) -> dict[str, Any]:
    return {"items": items, "total_count": count}
