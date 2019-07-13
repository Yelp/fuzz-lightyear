import pytest

from fuzzer_core.client import get_client
from testing import mock_server as mock_server_module


@pytest.fixture(scope='session')
def mock_server():
    with mock_server_module.vulnerable_server():
        yield


@pytest.fixture(scope='session')
def mock_schema(mock_server):
    yield mock_server_module.get_mock_schema()


@pytest.fixture(scope='session')
def mock_client(mock_schema):
    return get_client(mock_server_module.URL, mock_schema)
