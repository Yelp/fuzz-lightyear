import pytest

import fuzz_lightyear


@pytest.fixture
def mock_api_client(mock_client):
    """
    Override victim and attacker account, with proper API keys.
    """
    victim_key = mock_client.user.post_create_user().result()
    attacker_key = mock_client.user.post_create_user().result()

    fuzz_lightyear.victim_account(
        lambda: {
            '_request_options': {
                'headers': {
                    'X-API-KEY': victim_key,
                },
            },
        },
    )
    fuzz_lightyear.attacker_account(
        lambda: {
            '_request_options': {
                'headers': {
                    'X-API-KEY': attacker_key,
                },
            },
        },
    )

    yield mock_client
