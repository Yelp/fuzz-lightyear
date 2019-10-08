import pytest

from fuzz_lightyear.request import FuzzingRequest
from fuzz_lightyear.response import ResponseSequence
from fuzz_lightyear.runner import run_sequence


def test_basic(mock_client):
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


def test_skipped_due_to_no_inputs(mock_client):
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


@pytest.mark.xfail(
    reason='https://github.com/Yelp/fuzz-lightyear/issues/11',
)
def test_side_effect(mock_api_client):
    responses = run_sequence(
        [
            FuzzingRequest(
                tag='sequence',
                operation_id='post_create_with_side_effect',
            ),
            FuzzingRequest(
                tag='user',
                operation_id='get_get_user',
            ),

            # This goes last, to test for IDOR.
            FuzzingRequest(
                tag='sequence',
                operation_id='get_get_with_side_effect',
            ),
        ],
        ResponseSequence(),
    )

    assert responses.responses[1].has_created_resource
    assert responses.test_results['IDORPlugin']
