import pytest

from fuzzer_core.datastore import get_user_defined_mapping
from fuzzer_core.supplements.abstraction import get_abstraction
from testing import mock_server as mock_server_module


@pytest.fixture(autouse=True)
def clear_caches():
    get_abstraction.cache_clear()
    get_user_defined_mapping.cache_clear()


@pytest.fixture(scope='session')
def mock_server():
    with mock_server_module.vulnerable_server():
        yield


@pytest.fixture(scope='session')
def mock_schema(mock_server):
    yield mock_server.get_mock_schema()
