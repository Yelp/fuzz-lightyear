from collections import Counter

import pytest
from bravado.exception import HTTPError
from bravado_core.exception import SwaggerMappingError
from swagger_spec_validator.common import SwaggerValidationError

import fuzz_lightyear
from fuzz_lightyear.fuzzer import fuzz_parameters
from fuzz_lightyear.request import FuzzingRequest


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


class TestPredefinedFactory:
    def test_success(self, mock_client):
        def factory():
            return 1
        fuzz_lightyear.register_factory('id')(factory)

        request = FuzzingRequest(
            operation_id='get_public_listing',
            tag='basic',
        )

        request.send()

        assert request.fuzzed_input['id'] == 1

    def test_exclude_parameter(self, mock_client):
        def factory():
            return None
        fuzz_lightyear.register_factory('id')(factory)

        request = FuzzingRequest(
            operation_id='get_public_listing',
            tag='basic',
        )

        # id is a required parameter, so this will raise, if the id isn't
        # provided (as expected)
        with pytest.raises(SwaggerMappingError):
            request.send()


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

    factory = fuzz_parameters([('key', schema,)], 'get_public_listing')
    if is_required:
        assert_randomness(factory, [True, False])
    else:
        assert_randomness(factory, [None, True, False])


def test_integers(mock_client):
    schema = {
        'name': 'key',
        'type': 'integer',
        'minimum': 0,
        'maximum': 3,
        'exclusiveMaximum': True,
    }

    factory = fuzz_parameters([('key', schema,)], 'get_public_listing')

    assert_randomness(factory, [None, 0, 1, 2, ])


class TestArray:

    def test_basic(self, mock_client):
        factory = fuzz_parameters(
            [(
                'key',
                {
                    'name': 'key',
                    'type': 'array',
                    'items': {
                        'type': 'boolean',
                    },
                },
            )], 'get_public_listing',
        )

        for _ in range(10):
            item_list = factory.example()['key']
            if item_list is None:
                continue

            for item in item_list:
                assert item in [None, True, False]

    def test_nested(self, mock_client):
        factory = fuzz_parameters(
            [(
                'key',
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
            )], 'get_public_listing',
        )

        for _ in range(10):
            for parent_list in factory.example()['key']:
                if parent_list is None:
                    # This is possible, because it's not required.
                    continue

                for item in parent_list:
                    assert item in [None, True, False]


class TestObject:

    def test_basic(self, mock_client):
        factory = fuzz_parameters(
            [(
                'key',
                {
                    'name': 'key',
                    'type': 'object',
                    'required': [
                        'b',
                    ],
                    'properties': {
                        'a': {
                            'type': 'boolean',
                        },
                        'b': {
                            'type': 'boolean',
                        },
                    },
                },
            )], 'get_public_listing',
        )

        for _ in range(10):
            obj = factory.example()['key']
            assert obj['a'] in [None, True, False]
            assert obj['b'] in [True, False]

    def test_nested(self, mock_client):
        def factory():
            return 'test_value'
        fuzz_lightyear.register_factory('session')(factory)

        request = FuzzingRequest(
            operation_id='post_nested_model',
            tag='complex',
        )

        request.send()

        assert request.fuzzed_input['payload']['info']['session'] == 'test_value'


class TestInvalidSchema:

    def test_no_type(self):
        with pytest.raises(SwaggerValidationError):
            fuzz_parameters(
                [(
                    'no_type_parameter',
                    {
                        'name': 'no_type_parameter',
                    },
                )], 'get_public_listing',
            )


class TestEnumeration:

    def test(self):
        factory = fuzz_parameters(
            [(
                'key',
                {
                    'type': 'string',
                    'enum': ['foo', 'bar'],
                },
            )], 'get_public_listing',
        )

        assert_randomness(factory, ['foo', 'bar'])

    def test_fixture(self):
        def factory():
            return 'qux'
        fuzz_lightyear.register_factory('enumerated_field')(factory)

        factory = fuzz_parameters(
            [(
                'enumerated_field',
                {
                    'name': 'enumerated_field',
                    'type': 'string',
                    'enum': ['foo', 'bar'],
                    'required': True,
                },
            )], 'get_public_listing',
        )

        assert factory.example()['enumerated_field'] == 'qux'


def assert_randomness(strategy, expected_values):
    n = 10
    counter = Counter()
    for _ in range(n):
        counter[strategy.example()['key']] += 1

    for key in counter.keys():
        assert key in expected_values

    assert counter.most_common(1)[0][1] < n
