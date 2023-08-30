from typing import Any, Callable, Iterator

from pydantic import BaseModel
from sqlalchemy import func

from app.common.exceptions import InvalidFilterField, InvalidFilterType, InvalidSortField

_OPERATORS_MAP = {
    "lte": lambda model_value, filter_value: model_value <= filter_value,
    "gte": lambda model_value, filter_value: model_value >= filter_value,
    "icontains": lambda model_value, filter_value: func.lower(model_value).contains(func.lower(filter_value)),
    "exact": lambda model_value, filter_value: model_value == filter_value,
}


def _get_filter_function(filter_type: str) -> Callable:
    filter_function = _OPERATORS_MAP.get(filter_type)
    if filter_function is None:
        raise InvalidFilterType
    return filter_function


class BaseFilter(BaseModel):
    class Constants:
        model: Any

    @property
    def filters(self) -> list:
        filter_values = self.model_dump(exclude_none=True)
        filters = []
        for key, value in filter_values.items():
            field, lookup = key.split("__")
            filter_function = _get_filter_function(lookup)
            model_field = self._get_model_field(field)
            filter_ = filter_function(model_field, value)
            filters.append(filter_)
        return filters

    def _get_model_field(self, field_name: str) -> Any:
        model_field = getattr(self.Constants.model, field_name, None)
        if model_field is None:
            raise InvalidFilterField
        return model_field


class BaseSorter(BaseModel):
    sort_by: str | None = None

    class Constants:
        model: Any
        order_by_fields: list[str]

    @property
    def order_by(self) -> list:
        ordering_rules: list[Any] = []
        if not self.sort_by:
            return ordering_rules
        sortable_fields = self._get_sortable_fields(self.sort_by)
        for field, descending in sortable_fields:
            model_field = getattr(self.Constants.model, field)
            rule = model_field.desc() if descending else model_field.asc()
            ordering_rules.append(rule)
        return ordering_rules

    def _get_sortable_fields(self, fields_raw: str) -> Iterator[tuple[str, bool]]:
        fields_list = fields_raw.split(",")
        for field in fields_list:
            descending = field.startswith("-")
            field_name = field[1:] if descending else field
            if field_name not in self.Constants.order_by_fields:
                raise InvalidSortField()
            yield field_name, descending
