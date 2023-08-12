from typing import Any

from pydantic import BaseModel
from sqlalchemy import func

_OPERATORS_MAP = {
    "lte": lambda model_value, filter_value: model_value <= filter_value,
    "gte": lambda model_value, filter_value: model_value >= filter_value,
    "icontains": lambda model_value, filter_value: func.lower(model_value).contains(func.lower(filter_value)),
    "exact": lambda model_value, filter_value: model_value == filter_value,
}


class BaseFilter(BaseModel):
    class Constants:
        model: Any

    @property
    def filters(self) -> list:
        schema = self.model_dump(exclude_none=True)
        filters = []
        for key, value in schema.items():
            field, lookup = key.split("__")
            filter_ = _OPERATORS_MAP[lookup](getattr(self.Constants.model, field), value)
            filters.append(filter_)
        return filters
