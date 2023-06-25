from typing import Any, Dict, Generic, List, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
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
        return db.query(self.model).filter(self.model.id == id_).first()

    def get_all(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Model]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchema) -> Model:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Model, obj_in: Union[UpdateSchema, Dict[str, Any]]) -> Model:
        obj_data = jsonable_encoder(obj_in)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id_: int) -> Model | None:
        obj = db.query(self.model).get(id_)
        db.delete(obj)
        db.commit()
        return obj
