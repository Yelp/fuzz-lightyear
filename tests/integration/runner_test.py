import pytest
from bravado.exception import HTTPError

import fuzz_lightyear
from fuzz_lightyear.request import FuzzingRequest
from fuzz_lightyear.response import ResponseSequence
from fuzz_lightyear.runner import run_sequence


@pytest.fixture
def non_vulnerable_operations(request):
    if not isinstance(request.param, list):
        raise ValueError

    def get_exclusions():
        return request.param

    fuzz_lightyear.exclusions.non_vulnerable_operations(get_exclusions)
    yield


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


def test_valid_request_skip_idor_no_inputs(mock_client):
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


@pytest.mark.parametrize(
    'non_vulnerable_operations',
    [
        (['get_public_listing']),
        (['basic.get_public_listing']),
    ],
    indirect=['non_vulnerable_operations'],
)
def test_valid_request_skip_idor_manually_excluded(
    mock_client,
    non_vulnerable_operations,
):
    responses = run_sequence(
        [
            FuzzingRequest(
                tag='basic',
                operation_id='get_public_listing',
            ),
        ],
        ResponseSequence(),
    )

    assert isinstance(responses.data['value'], str)
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


class TestStatefulSequence:

    def test_basic(self, mock_client):
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

    def test_single_factory_usage(self, mock_client):
        current_id = 1234

        def create_resource():
            nonlocal current_id
            output = current_id
            current_id += 1

            return output
        fuzz_lightyear.register_factory('id')(create_resource)
        responses = run_sequence(
            [
                FuzzingRequest(
                    tag='sequence',
                    operation_id='post_bravo_one',
                ),
                FuzzingRequest(
                    tag='sequence',
                    operation_id='get_bravo_two',
                ),
            ],
            ResponseSequence(),
        )

        assert responses.responses[-1] == 1234
        assert current_id != 1234
