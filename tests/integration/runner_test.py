import pytest
from bravado.exception import HTTPError

from fuzz_lightyear.request import FuzzingRequest
from fuzz_lightyear.response import ResponseSequence
from fuzz_lightyear.runner import run_sequence


def test_invalid_request(mock_client):
    with pytest.raises(HTTPError):
        run_sequence(
            [
                FuzzingRequest(
                    tag='constant',
                    operation_id='get_will_throw_error',
                    code=400,
                ),
            ],
            ResponseSequence(),
        )


def test_valid_request_skip_idor(mock_client):
    responses = run_sequence(
        [
            FuzzingRequest(
                tag='basic',
                operation_id='get_no_inputs_required',
            ),
        ],
        ResponseSequence(),
    )

    assert responses.data['session'] == 'victim_session'
    assert responses.test_results == {}


def test_valid_request_with_idor(mock_client):
    responses = run_sequence(
        [
            FuzzingRequest(
                tag='basic',
                operation_id='get_private_listing',
                id=1,
            ),
        ],
        ResponseSequence(),
    )

    assert responses.data['session'] == 'victim_session'
    assert responses.test_results['IDORPlugin']


def test_stateful_sequence(mock_client):
    responses = run_sequence(
        [
            FuzzingRequest(
                tag='sequence',
                operation_id='post_alpha_one',
            ),
            FuzzingRequest(
                tag='sequence',
                operation_id='get_alpha_two',
            ),
        ],
        ResponseSequence(),
    )

    # This value is returned from `post_alpha_one`. If they were
    # independently fuzzed, it would not be this value.
    assert responses.responses[-1] == 'ok'
