import pytest

import fuzz_lightyear
from fuzz_lightyear.client import get_client
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
    fuzz_lightyear.victim_account(
        lambda: {
            '_request_options': {
                'headers': {
                    'Cookie': 'session=victim_session',
                },
            },
        },
    )
    fuzz_lightyear.attacker_account(
        lambda: {
            '_request_options': {
                'headers': {
                    'Cookie': 'session=attacker_session',
                },
            },
        },
    )
    yield get_client(mock_server_module.URL, mock_schema)
