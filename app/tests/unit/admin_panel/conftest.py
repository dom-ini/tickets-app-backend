from unittest.mock import Mock

import pytest


@pytest.fixture(name="mock_request")
def get_mock_request() -> Mock:
    return Mock()
