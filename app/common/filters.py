from typing import Any, Iterator

from pydantic import BaseModel
from sqlalchemy import func

from app.common.exceptions import InvalidSortField

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


class BaseSorter(BaseModel):
    sort_by: str | None = None

    class Constants:
        model: Any
        order_by_fields: list[str]

    @property
    def order_by(self) -> list:
        rules: list[Any] = []
        if not self.sort_by:
            return rules
        sortable_fields = self._get_sortable_fields(self.sort_by)
        for field, descending in sortable_fields:
            model_field = getattr(self.Constants.model, field)
            rule = model_field.desc() if descending else model_field.asc()
            rules.append(rule)
        return rules

    def _get_sortable_fields(self, fields_raw: str) -> Iterator[tuple[str, bool]]:
        fields_list = fields_raw.split(",")
        for field in fields_list:
            descending = field.startswith("-")
            field_name = field[1:] if descending else field
            if field_name not in self.Constants.order_by_fields:
                raise InvalidSortField()
            yield field_name, descending
