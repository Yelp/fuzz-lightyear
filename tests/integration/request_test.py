import pytest

from fuzzer_core.request import FuzzingRequest
from fuzzer_core.supplements.abstraction import get_abstraction


def test_send_basic_request(mock_client):
    request = FuzzingRequest(
        operation_id='get_no_inputs_required',
        tag='basic',
    )

    assert request.send().session == 'victim_session'


def test_send_specified_auth(mock_client):
    request = FuzzingRequest(
        operation_id='get_no_inputs_required',
        tag='basic',
    )

    assert request.send(
        auth=get_abstraction().get_attacker_session(),
    ).session == 'attacker_session'


@pytest.mark.parametrize(
    'id',
    (
        'get_expect_primitives',
        'get_expect_array',
        'post_expect_array',
    ),
)
def test_fuzzed_request(id, mock_client):
    request = FuzzingRequest(
        tag='types',
        operation_id=id,
    )
    response = request.send()

    assert response.value == 'ok'
