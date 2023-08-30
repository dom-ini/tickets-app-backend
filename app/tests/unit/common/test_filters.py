# mypy: disable-error-code="attr-defined, misc, assignment, method-assign"
from unittest.mock import Mock

import pytest

from app.common.exceptions import InvalidFilterField, InvalidFilterType, InvalidSortField
from app.common.filters import BaseFilter, BaseSorter


@pytest.fixture(name="mock_model")
def get_mock_model() -> Mock:
    return Mock()


@pytest.fixture(name="filter_instance")
def get_filter_instance(mock_model: Mock) -> BaseFilter:
    class Constants:
        model = mock_model

    BaseFilter.Constants = Constants
    BaseFilter.model_dump = Mock()
    return BaseFilter()


@pytest.fixture(name="sorter_instance")
def get_sorter_instance(mock_model: Mock) -> BaseSorter:
    class Constants:
        model = mock_model
        order_by_fields: list[str] = []

    BaseSorter.Constants = Constants
    return BaseSorter()


def test_filters(filter_instance: BaseFilter) -> None:
    filter_instance.model_dump.return_value = {"field__icontains": "", "other__exact": ""}

    result = filter_instance.filters

    assert len(result) == 2


def test_filters_with_invalid_filter_type_should_raise_error(filter_instance: BaseFilter) -> None:
    filter_instance.model_dump.return_value = {"field__incorrect": ""}

    with pytest.raises(InvalidFilterType):
        _ = filter_instance.filters


def test_filters_with_invalid_filter_field_should_raise_error(filter_instance: BaseFilter, mock_model: Mock) -> None:
    filter_instance.model_dump.return_value = {"field__exact": ""}
    mock_model.field = None

    with pytest.raises(InvalidFilterField):
        _ = filter_instance.filters


def test_order_by(sorter_instance: BaseSorter) -> None:
    sorter_instance.Constants.order_by_fields = ["name"]
    sorter_instance.sort_by = "name"

    result = sorter_instance.order_by

    assert len(result) == 1


def test_order_by_with_invalid_sorting_field_should_raise_error(sorter_instance: BaseSorter) -> None:
    sorter_instance.Constants.order_by_fields = ["name"]
    sorter_instance.sort_by = "invalid"

    with pytest.raises(InvalidSortField):
        _ = sorter_instance.order_by


def test_order_by_with_no_ordering_specified(sorter_instance: BaseSorter) -> None:
    sorter_instance.Constants.order_by_fields = ["name"]
    sorter_instance.sort_by = None

    result = sorter_instance.order_by

    assert len(result) == 0
