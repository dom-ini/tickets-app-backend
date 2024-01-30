from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.common.utils import InstanceInDBValidator
from app.tests.unit.common.conftest import Model, SampleCRUD


class CustomException(Exception):
    pass


@pytest.fixture(name="mock_instance_validator", scope="session")
def get_mock_instance_validator(mock_crud: SampleCRUD) -> InstanceInDBValidator:
    return InstanceInDBValidator[Model, SampleCRUD](mock_crud, CustomException)  # type: ignore[type-var, arg-type]


def test_instance_or_404_with_instance(mock_instance_validator: InstanceInDBValidator) -> None:
    instance = Model()

    result = mock_instance_validator.instance_or_404(instance)

    assert result == instance


def test_instance_or_404_without_instance_should_raise_exception(
    mock_instance_validator: InstanceInDBValidator,
) -> None:
    with pytest.raises(CustomException):
        mock_instance_validator.instance_or_404(None)


def test_by_id_should_call_crud_method(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    instance_id = 1
    mock_get = mocker.patch.object(mock_crud, attribute="get")

    mock_instance_validator.by_id(mock_db, id_=instance_id)

    mock_get.assert_called_once_with(mock_db, id_=instance_id)


def test_by_id_with_instance(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    instance = Model()
    mocker.patch.object(mock_crud, attribute="get", return_value=instance)

    result = mock_instance_validator.by_id(mock_db, id_=1)

    assert result == instance


def test_by_id_without_instance_should_raise_exception(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    mocker.patch.object(mock_crud, attribute="get", return_value=None)

    with pytest.raises(CustomException):
        mock_instance_validator.by_id(mock_db, id_=1)


def test_by_slug_should_call_crud_method(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    instance_slug = "slug"
    mock_get = mocker.patch.object(mock_crud, attribute="get_by_slug")

    mock_instance_validator.by_slug(mock_db, slug=instance_slug)

    mock_get.assert_called_once_with(mock_db, slug=instance_slug)


def test_by_slug_should_fail_if_crud_service_does_not_have_get_by_slug_method(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    mocker.patch.object(mock_crud, attribute="get_by_slug", side_effect=NotImplementedError)

    with pytest.raises(NotImplementedError):
        mock_instance_validator.by_slug(mock_db, slug="slug")


def test_by_slug_with_instance(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    instance = Model()
    mocker.patch.object(mock_crud, attribute="get_by_slug", return_value=instance)

    result = mock_instance_validator.by_slug(mock_db, slug="slug")

    assert result == instance


def test_by_slug_without_instance_should_raise_exception(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    mocker.patch.object(mock_crud, attribute="get_by_slug", return_value=None)

    with pytest.raises(CustomException):
        mock_instance_validator.by_slug(mock_db, slug="slug")


def test_by_token_should_call_crud_method(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    token = "token"
    mock_get = mocker.patch.object(mock_crud, attribute="get_by_token")

    mock_instance_validator.by_token(mock_db, token=token)

    mock_get.assert_called_once_with(mock_db, token=token)


def test_by_token_should_fail_if_crud_service_does_not_have_get_by_token_method(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    mocker.patch.object(mock_crud, attribute="get_by_token", side_effect=NotImplementedError)

    with pytest.raises(NotImplementedError):
        mock_instance_validator.by_token(mock_db, token="token")


def test_by_token_with_instance(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    instance = Model()
    mocker.patch.object(mock_crud, attribute="get_by_token", return_value=instance)

    result = mock_instance_validator.by_token(mock_db, token="token")

    assert result == instance


def test_by_token_without_instance_should_raise_exception(
    mock_instance_validator: InstanceInDBValidator, mock_db: Mock, mock_crud: SampleCRUD, mocker: MockerFixture
) -> None:
    mocker.patch.object(mock_crud, attribute="get_by_token", return_value=None)

    with pytest.raises(CustomException):
        mock_instance_validator.by_token(mock_db, token="token")
