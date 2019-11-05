import pytest

import fuzz_lightyear
from fuzz_lightyear.request import FuzzingRequest
from fuzz_lightyear.supplements.abstraction import get_abstraction
from testing.mock_server import URL


def test_json(mock_client):
    request = FuzzingRequest(
        operation_id='post_various_locations',
        tag='location',
        path_id='path',
        query='a',
        form='b',
        header='c',
    )

    request.send()

    assert request.json() == {
        'method': 'POST',
        'path': '/location/path',
        'query': {
            'query': 'a',
        },
        'formData': {
            'form': 'b',
        },
        'header': {
            'header': 'c',
        },
    }
    assert str(request) == (
        f'curl -X POST {URL}/location/path?query=a '
        '--data \'form=b\' '
        '-H \'header: c\''
    )
    assert repr(request) == 'FuzzingRequest(location.post_various_locations)'


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


def test_str_encodes_array_path_parameters(mock_client):
    request = FuzzingRequest(
        operation_id='get_expect_path_array',
        tag='types',
        ids=[1, 2, 3],
    )
    request.send()
    assert str(request) == (
        f'curl -X GET {URL}/types/path_array/1%2C2%2C3'
    )


def test_str_encodes_array_query_parameters(mock_client):
    request = FuzzingRequest(
        operation_id='get_expect_array',
        tag='types',
        array=[
            True,
            False,
        ],
    )
    assert str(request) == f'curl -X GET {URL}/types/array?array=True&array=False'


@pytest.mark.parametrize(
    'tag, id',
    (
        ('types', 'get_expect_primitives',),
        ('types', 'get_expect_array',),
        ('types', 'post_expect_array',),
        ('types', 'put_expect_array',),
        ('location', 'post_body_parameter',),
    ),
)
def test_fuzzed_request(tag, id, mock_client):
    request = FuzzingRequest(
        tag=tag,
        operation_id=id,
    )
    response = request.send()

    assert response.value == 'ok'


@pytest.mark.parametrize(
    'decorator_args, fuzzing_request_args',
    [
        (
            {'tags': 'types'},
            {'operation_id': 'get_expect_primitives', 'tag': 'types'},
        ),
        (
            {},
            {'operation_id': 'get_expect_primitives', 'tag': 'types'},
        ),
    ],
)
def test_post_fuzz_hook(mock_client, decorator_args, fuzzing_request_args):
    def post_fuzz_hook(operation, fuzzed_input):
        new_input = fuzzed_input.copy()
        if '_request_options' not in new_input:
            new_input['_request_options'] = {}

        if 'headers' not in new_input['_request_options']:
            new_input['_request_options']['headers'] = {}

        new_input['_request_options']['headers']['__test__'] = 'test'
        return new_input

    fuzz_lightyear.hooks.post_fuzz(**decorator_args)(post_fuzz_hook)
    request = FuzzingRequest(**fuzzing_request_args)

    request.send()
    assert request.fuzzed_input['_request_options']['headers']['__test__'] == 'test'
