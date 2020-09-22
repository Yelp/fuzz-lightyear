import base64
import json
import os

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
        '-H \'header: c\' '
        '-H \'Cookie: session=victim_session\''
    )
    assert repr(request) == 'FuzzingRequest(location.post_various_locations)'


def test_send_basic_request(mock_client):
    request = FuzzingRequest(
        operation_id='get_no_inputs_required',
        tag='basic',
    )

    assert request.send().session == 'victim_session'


def test_send_body(mock_client):
    request = FuzzingRequest(
        operation_id='post_nested_model',
        tag='complex',
    )

    # We need to trigger the parameters to be fuzzed.
    request.send()

    assert str(request) == (
        f'curl -X POST {URL}/complex/nested '
        f'--data \'{json.dumps(request.fuzzed_input["payload"])}\' '
        '-H \'Content-Type: application/json\' '
        '-H \'Cookie: session=victim_session\''
    )


def test_send_specified_auth(mock_client):
    request = FuzzingRequest(
        operation_id='get_no_inputs_required',
        tag='basic',
    )

    assert request.send(
        auth=get_abstraction().get_attacker_session,
    ).session == 'attacker_session'


def test_send_endpoint_auth(mock_client):
    request = FuzzingRequest(
        operation_id='get_no_inputs_required',
        tag='basic',
    )

    fuzz_lightyear.attacker_account(
        lambda operation_id: {
            '_request_options': {
                'headers': {
                    'Cookie': 'session=' + operation_id,
                },
            },
        },
    )

    assert request.send(
        auth=get_abstraction().get_attacker_session,
    ).session == 'get_no_inputs_required'


def test_str_encodes_array_path_parameters(mock_client):
    request = FuzzingRequest(
        operation_id='get_expect_path_array',
        tag='types',
        ids=[1, 2, 3],
    )
    request.send()
    assert str(request) == (
        f'curl -X GET {URL}/types/path_array/1%2C2%2C3 '
        '-H \'Cookie: session=victim_session\''
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
    assert str(request) == (
        f'curl -X GET {URL}/types/array?array=True&array=False '
        '-H \'Cookie: session=victim_session\''
    )


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
    'decorator_args, fuzzing_request_args, expected_headers',
    [
        (
            {'tags': 'types'},
            {'operation_id': 'get_expect_primitives', 'tag': 'types'},
            {'__test__': 'test'},
        ),
        (
            {},
            {'operation_id': 'get_expect_primitives', 'tag': 'types'},
            {'__test__': 'test'},
        ),
        (
            {'tags': 'numbers'},
            {'operation_id': 'get_expect_primitives', 'tag': 'types'},
            {},
        ),
    ],
)
def test_post_fuzz_hook(
    mock_client,
    decorator_args,
    fuzzing_request_args,
    expected_headers,
):
    def post_fuzz_hook(operation, fuzzed_input):
        if '_request_options' not in fuzzed_input:
            fuzzed_input['_request_options'] = {}

        if 'headers' not in fuzzed_input['_request_options']:
            fuzzed_input['_request_options']['headers'] = {}

        fuzzed_input['_request_options']['headers']['__test__'] = 'test'

    fuzz_lightyear.hooks.post_fuzz(**decorator_args)(post_fuzz_hook)
    request = FuzzingRequest(**fuzzing_request_args)

    request.send()
    request_headers = request.fuzzed_input.get('_request_options', {}).get('headers', {})
    assert request_headers == expected_headers


@pytest.mark.parametrize(
    'decorator_args, fuzzing_request_args',
    [
        (
            {},
            {'operation_id': 'get_expect_primitives', 'tag': 'types'},
        ),
    ],
)
def test_multiple_post_fuzz_hooks(mock_client, decorator_args, fuzzing_request_args):
    def post_fuzz_hook_a(operation, fuzzed_input):
        if '_request_options' not in fuzzed_input:
            fuzzed_input['_request_options'] = {}

        if 'headers' not in fuzzed_input['_request_options']:
            fuzzed_input['_request_options']['headers'] = {}

        fuzzed_input['_request_options']['headers']['__a__'] = 'a'

    def post_fuzz_hook_b(operation, fuzzed_input):
        if '_request_options' not in fuzzed_input:
            fuzzed_input['_request_options'] = {}

        if 'headers' not in fuzzed_input['_request_options']:
            fuzzed_input['_request_options']['headers'] = {}

        fuzzed_input['_request_options']['headers']['__b__'] = 'b'

    fuzz_lightyear.hooks.post_fuzz(**decorator_args)(post_fuzz_hook_a)
    fuzz_lightyear.hooks.post_fuzz(**decorator_args)(post_fuzz_hook_b)
    request = FuzzingRequest(**fuzzing_request_args)

    request.send()

    request_headers = request.fuzzed_input.get('_request_options', {}).get('headers', {})
    assert request_headers['__a__'] == 'a'
    assert request_headers['__b__'] == 'b'


@pytest.mark.parametrize(
    'decorator_args, fuzzing_request_args',
    [
        (
            {'rerun': True},
            {'operation_id': 'get_expect_primitives', 'tag': 'types'},
        ),
    ],
)
def test_rerun_post_fuzz_hook(mock_client, decorator_args, fuzzing_request_args):
    def nonce_post_fuzz_hook(operation, fuzzed_input):
        if '_request_options' not in fuzzed_input:
            fuzzed_input['_request_options'] = {}

        if 'headers' not in fuzzed_input['_request_options']:
            fuzzed_input['_request_options']['headers'] = {}

        fuzzed_input['_request_options']['headers']['__nonce__'] = \
            base64.b64encode(os.urandom(4)).decode()

    fuzz_lightyear.hooks.post_fuzz(**decorator_args)(nonce_post_fuzz_hook)
    request = FuzzingRequest(**fuzzing_request_args)

    request.send()
    original_nonce = request.fuzzed_input['_request_options']['headers']['__nonce__']

    request.send()
    new_nonce = request.fuzzed_input['_request_options']['headers']['__nonce__']

    assert new_nonce != original_nonce
