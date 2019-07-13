import pytest

from fuzzer_core.datastore import get_user_defined_mapping
from testing import mock_server


@pytest.fixture(autouse=True)
def clear_caches():
    get_user_defined_mapping.cache_clear()


@pytest.fixture(scope='session')
def mock_schema():
    with mock_server.vulnerable_server():
        yield mock_server.get_mock_schema()
