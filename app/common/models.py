from typing import Annotated

from sqlalchemy.orm import mapped_column  # type: ignore[attr-defined]

IntPk = Annotated[int, mapped_column(primary_key=True, index=True)]
UniqueIndexedStr = Annotated[str, mapped_column(unique=True, index=True, nullable=False)]
BoolFalse = Annotated[bool, mapped_column(default=False)]
