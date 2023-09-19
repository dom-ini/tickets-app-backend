from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app.auth.models import User
from app.tests.unit.utils import create_user_instance


@pytest.fixture()
def mock_db() -> Mock:
    return Mock(spec=Session)


@pytest.fixture(name="user_instance")
def get_user_instance() -> User:
    user = create_user_instance()
    return user
