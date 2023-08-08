from fastapi import HTTPException

from app.common.crud import CreateSchema, CRUDBase, Model, UpdateSchema
from app.common.deps import DBSession


def validate_instance_id(
    db: DBSession,
    id_: int,
    crud_service: CRUDBase[Model, CreateSchema, UpdateSchema],
    not_found_exception: HTTPException,
) -> Model:
    instance = crud_service.get(db, id_=id_)
    if not instance:
        raise not_found_exception
    return instance
