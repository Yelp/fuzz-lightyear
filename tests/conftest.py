import pytest

from testing import mock_server


@pytest.fixture(scope='session')
def mock_schema():
    with mock_server.vulnerable_server():
        yield mock_server.get_mock_schema()
