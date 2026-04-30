from sqlalchemy.orm import DeclarativeBase, declared_attr  # type: ignore[attr-defined]


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(self) -> str:
        return self.__name__.lower()
