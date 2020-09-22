import pytest
from bravado.exception import HTTPError

from fuzz_lightyear.request import FuzzingRequest
from fuzz_lightyear.result import FuzzingResult
from fuzz_lightyear.runner import validate_sequence


@pytest.mark.parametrize(
    'sequence',
    (
        [
            FuzzingRequest(
                tag='sequence',
                operation_id='post_alpha_one',
            ),
        ],
        [
            FuzzingRequest(
                tag='sequence',
                operation_id='get_alpha_two',
            ),
        ],
    ),
)
def test_successful_sequence(mock_client, sequence):
    result = FuzzingResult(sequence)
    validate_sequence(result.requests, result.responses)

    assert result.is_successful()


def test_failed_sequence_should_not_be_successful(mock_client):
    result = FuzzingResult([
        FuzzingRequest(
            tag='sequence',
            operation_id='post_alpha_one',
        ),
        FuzzingRequest(
            tag='constant',
            operation_id='get_will_throw_error',
        ),
        FuzzingRequest(
            tag='sequence',
            operation_id='get_alpha_two',
        ),
    ])

    with pytest.raises(HTTPError):
        validate_sequence(result.requests, result.responses)

    assert not result.is_successful()
