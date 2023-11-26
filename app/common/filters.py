import dataclasses
from typing import Any, Callable, Iterator

from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import class_mapper

from app.common.exceptions import InvalidFilterField, InvalidFilterType, InvalidSortField

_OPERATORS_MAP = {
    "lte": lambda model_value, filter_value: model_value <= filter_value,
    "gte": lambda model_value, filter_value: model_value >= filter_value,
    "icontains": lambda model_value, filter_value: func.lower(model_value).contains(func.lower(filter_value)),
    "exact": lambda model_value, filter_value: model_value == filter_value,
}


@dataclasses.dataclass
class ModelFilters:
    """
    Class for storing SQL Alchemy filters and relationships to include in JOIN statement if needed
    """

    statements: list
    related: list


def _get_filter_function(filter_type: str) -> Callable:
    filter_function = _OPERATORS_MAP.get(filter_type)
    if filter_function is None:
        raise InvalidFilterType
    return filter_function


class BaseFilter(BaseModel):
    class Constants:
        model: Any

    @property
    def filters(self) -> ModelFilters:
        filter_values = self.model_dump(exclude_none=True)
        filters = []
        models_to_join = []
        for key, value in filter_values.items():
            field_name, *nested, lookup = key.split("__")
            nested_field_name = nested[0] if nested else None
            filter_ = self._get_filter(lookup, field_name, nested_field_name, value)
            filters.append(filter_)
            if nested_field_name:
                to_join = self._get_model_to_join(field_name)
                models_to_join.append(to_join)
        return ModelFilters(statements=filters, related=models_to_join)

    def _get_filter(self, lookup: str, field_name: str, nested_field_name: str | None, filter_value: Any) -> Any:
        filter_function = _get_filter_function(lookup)
        model_field = self._get_field_reference(field_name, nested_field_name)
        filter_ = filter_function(model_field, filter_value)
        is_many_to_many = self._check_if_many_to_many(field_name)
        if not is_many_to_many:
            return filter_
        wrapped_filter = self._get_many_to_many_filter(field_name, filter_)
        return wrapped_filter

    def _get_model_to_join(self, field_name: str) -> Any:
        return getattr(self.Constants.model, field_name)

    def _get_field_reference(self, field_name: str, nested_field_name: str | None = None) -> Any:
        if nested_field_name is not None:
            model_field = self._get_model_field_from_relation(field_name, nested_field_name)
        else:
            model_field = getattr(self.Constants.model, field_name, None)
        if model_field is None:
            raise InvalidFilterField
        return model_field

    def _get_model_field_from_relation(self, relationship_name: str, nested_field_name: str) -> Any:
        relationship = getattr(self.Constants.model, relationship_name, None)
        if relationship is None:
            raise InvalidFilterField
        return getattr(relationship.mapper.class_, nested_field_name)

    def _check_if_many_to_many(self, field_name: str) -> bool:
        mapper = class_mapper(self.Constants.model)
        field = mapper.get_property(field_name)
        secondary = getattr(field, "secondary", None)
        return secondary is not None

    def _get_many_to_many_filter(self, relation_name: str, filter_: Callable) -> Callable:
        field = self._get_field_reference(field_name=relation_name)
        return field.any(filter_)


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
                raise InvalidSortField
            yield field_name, descending
