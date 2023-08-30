from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def mock_db() -> Mock:
    return Mock(spec=Session)
