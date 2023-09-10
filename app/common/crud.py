import secrets
from typing import Any, Generic, Iterable, Sequence, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base_class import Base

Model = TypeVar("Model", bound=Base)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class CRUDBase(Generic[Model, CreateSchema, UpdateSchema]):
    def __init__(self, model: Type[Model]):
        """
        CRUD object with default methods to Create, Read, Update and Delete

        :param model: a SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id_: Any) -> Model | None:
        query = select(self.model).where(self.model.id == id_)
        result = db.execute(query)
        return result.scalar()

    def get_all(self, db: Session, *, skip: int = 0, limit: int = 100) -> Sequence[Model]:
        query = select(self.model).offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()

    def create(self, db: Session, *, obj_in: CreateSchema) -> Model:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Model, obj_in: UpdateSchema | dict[str, Any]) -> Model:
        obj_data = jsonable_encoder(obj_in)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id_: int) -> Model | None:
        obj = self.get(db, id_=id_)
        db.delete(obj)
        db.commit()
        return obj


class SlugMixin(Generic[Model]):
    model: Type[Model]

    def get_by_slug(self, db: Session, slug: str) -> Model | None:
        query = select(self.model).where(self.model.slug == slug)
        result = db.execute(query)
        return result.scalar()


class FilterableMixin(Generic[Model]):
    model: Type[Model]

    def get_filtered(
        self,
        db: Session,
        *,
        filters: Iterable | None = None,
        order_by: Iterable | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Model]:
        query = select(self.model)
        if filters:
            query = query.where(*filters)
        if order_by:
            query = query.order_by(*order_by)
        query = query.offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()


def generate_unique_token(db: Session, *, token_model: Type[Model], payload: dict[str, Any]) -> Model:
    while True:
        value = secrets.token_urlsafe(64)
        instance = token_model(**payload, value=value)
        db.add(instance)
        try:
            db.commit()
            break
        except IntegrityError:
            db.rollback()
    return instance
