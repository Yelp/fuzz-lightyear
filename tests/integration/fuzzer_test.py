from collections import Counter

import pytest
from bravado.exception import HTTPError
from swagger_spec_validator.common import SwaggerValidationError

import fuzzer_core
from fuzzer_core.fuzzer import fuzz_parameters
from fuzzer_core.request import FuzzingRequest


def test_fuzz_enum(mock_client):
    request = FuzzingRequest(
        operation_id='get_will_throw_error',
        tag='constant',
    )

    with pytest.raises(HTTPError):
        request.send()

    assert request.fuzzed_input['code'] in [
        400,
        401,
        403,
        404,
        500,
    ]


def test_predefined_factory(mock_client):
    def factory():
        return 1
    fuzzer_core.register_factory('id')(factory)

    request = FuzzingRequest(
        operation_id='get_public_listing',
        tag='basic',
    )

    request.send()

    assert request.fuzzed_input['id'] == 1


@pytest.mark.parametrize(
    'is_required',
    (
        True,
        False,
        None,
    ),
)
def test_booleans(mock_client, is_required):
    schema = {
        'name': 'key',
        'type': 'boolean',
    }
    if is_required:
        schema['required'] = True
    elif is_required is False:
        schema['required'] = False

    factory = fuzz_parameters([schema])
    if is_required:
        assert_randomness(factory, [True, False])
    else:
        assert_randomness(factory, [None, True, False])


class TestArray:

    def test_basic(self, mock_client):
        factory = fuzz_parameters([
            {
                'name': 'key',
                'type': 'array',
                'items': {
                    'type': 'boolean',
                },
            },
        ])

        for _ in range(10):
            item_list = factory.example()['key']
            if item_list is None:
                continue

            for item in item_list:
                assert item in [None, True, False]

    def test_nested(self, mock_client):
        factory = fuzz_parameters([
            {
                'name': 'key',
                'type': 'array',
                'required': True,
                'items': {
                    # This is the `parent_list`
                    'type': 'array',
                    'items': {
                        'type': 'boolean',
                        'required': False,
                    },
                },
            },
        ])

        for _ in range(10):
            for parent_list in factory.example()['key']:
                if parent_list is None:
                    # This is possible, because it's not required.
                    continue

                for item in parent_list:
                    assert item in [None, True, False]


class TestObject:

    def test_basic(self, mock_client):
        factory = fuzz_parameters([
            {
                'name': 'key',
                'type': 'object',
                'required': True,
                'properties': {
                    'a': {
                        'type': 'boolean',
                    },
                    'b': {
                        'type': 'boolean',
                        'required': True,
                    },
                },
            },
        ])

        for _ in range(10):
            obj = factory.example()['key']
            assert obj['a'] in [None, True, False]
            assert obj['b'] in [True, False]


class TestInvalidSchema:

    def test_no_type(self):
        with pytest.raises(SwaggerValidationError):
            fuzz_parameters([
                {
                    'name': 'no_type_parameter',
                },
            ])


def assert_randomness(strategy, expected_values):
    n = 10
    counter = Counter()
    for _ in range(n):
        counter[strategy.example()['key']] += 1

    for key in counter.keys():
        assert key in expected_values

    assert counter.most_common(1)[0][1] < n
