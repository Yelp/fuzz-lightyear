import pytest

import fuzzer_core
from fuzzer_core.client import get_client
from testing import mock_server as mock_server_module


@pytest.fixture(scope='session')
def mock_server():
    with mock_server_module.vulnerable_server():
        yield


@pytest.fixture(scope='session')
def mock_schema(mock_server):
    yield mock_server_module.get_mock_schema()


@pytest.fixture
def mock_client(mock_schema):
    fuzzer_core.victim_account(
        lambda: {
            '_request_options': {
                'headers': {
                    'Cookie': 'session=victim_session',
                },
            },
        },
    )
    fuzzer_core.attacker_account(
        lambda: {
            '_request_options': {
                'headers': {
                    'Cookie': 'session=attacker_session',
                },
            },
        },
    )
    yield get_client(mock_server_module.URL, mock_schema)
