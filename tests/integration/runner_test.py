import pytest
from bravado.exception import HTTPError

from fuzzer_core.request import FuzzingRequest
from fuzzer_core.response import ResponseSequence
from fuzzer_core.runner import run_sequence


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
