from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError

from app.common.crud import generate_unique_token
from app.tests.unit.common.conftest import CreateSchema, Model, SampleCRUD, UpdateSchema


@pytest.fixture(name="mock_select")
def get_mock_select(mocker: MockerFixture) -> Mock:
    return mocker.patch("app.common.crud.select", return_value=Mock())


def test_get(mock_db: Mock, mock_crud: SampleCRUD, mock_select: Mock) -> None:
    mock_crud.get(mock_db, id_=1)

    mock_select.assert_called_with(mock_crud.model)


def test_get_all(mock_db: Mock, mock_crud: SampleCRUD, mock_select: Mock) -> None:
    mock_crud.get_all(mock_db)

    mock_select.assert_called_with(mock_crud.model)


@pytest.mark.parametrize("method_name", ["get_all", "get_filtered"])
def test_get_multiple_with_skip_and_limit(
    mock_db: Mock, mock_crud: SampleCRUD, mock_select: Mock, method_name: str
) -> None:
    skip = 1
    limit = 2
    method = getattr(mock_crud, method_name)

    method(mock_db, skip=skip, limit=limit)

    mock_select.return_value.offset.assert_called_once_with(skip)
    mock_select.return_value.offset.return_value.limit.assert_called_once_with(limit)


def test_create(mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture) -> None:
    obj_in = CreateSchema()
    mock_jsonable_encoder = mocker.patch("app.common.crud.jsonable_encoder")

    result = mock_crud.create(mock_db, obj_in=obj_in)

    assert isinstance(result, Model)
    mock_jsonable_encoder.assert_called_once_with(obj_in)


@pytest.mark.parametrize("obj_in", [(UpdateSchema()), {"key": "value"}])
def test_update(mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture, obj_in: dict | UpdateSchema) -> None:
    mock_jsonable_encoder = mocker.patch("app.common.crud.jsonable_encoder")
    db_obj = Model()

    result = mock_crud.update(mock_db, db_obj=db_obj, obj_in=obj_in)

    assert result == db_obj
    mock_jsonable_encoder.assert_called_once_with(obj_in)


def test_remove(mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture) -> None:
    instance = Model()
    instance_id = 1
    mock_get = mocker.patch.object(mock_crud, attribute="get", return_value=instance)

    result = mock_crud.remove(mock_db, id_=instance_id)

    assert result == instance
    mock_get.assert_called_once_with(mock_db, id_=instance_id)


def test_get_by_slug(mock_db: Mock, mock_crud: SampleCRUD, mock_select: Mock) -> None:
    mock_crud.get_by_slug(mock_db, slug="slug")

    mock_select.assert_called_once_with(mock_crud.model)


def test_get_filtered_with_filters(mock_db: Mock, mock_crud: SampleCRUD, mock_select: Mock) -> None:
    filters = [1, 2, 3]

    mock_crud.get_filtered(mock_db, filters=filters)

    mock_select.return_value.where.assert_called_once_with(*filters)


def test_get_filtered_with_ordering(mock_db: Mock, mock_crud: SampleCRUD, mock_select: Mock) -> None:
    order_by = [1, 2, 3]

    mock_crud.get_filtered(mock_db, order_by=order_by)

    mock_select.return_value.order_by.assert_called_once_with(*order_by)


def test_generate_unique_token_should_rollback_on_integrity_error(mock_db: Mock) -> None:
    mock_db.commit.side_effect = [IntegrityError("IntegrityError raised", orig=BaseException(), params=None), None]
    generate_unique_token(mock_db, token_model=Mock, payload={})

    mock_db.rollback.assert_called_once()
