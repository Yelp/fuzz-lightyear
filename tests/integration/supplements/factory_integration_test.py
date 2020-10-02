import fuzz_lightyear
from fuzz_lightyear.request import FuzzingRequest


def test_type_hinting(mock_client):
    def factory():
        return 1
    fuzz_lightyear.register_factory('string, integer')(factory)

    request = FuzzingRequest(
        operation_id='get_expect_primitives',
        tag='types',
    )

    request.send()

    assert request.fuzzed_input['string'] == '1'
    assert request.fuzzed_input['integer'] == 1


def test_endpoint_specific(mock_client):
    def factory():
        return 1

    def other_factory():
        return 2

    fuzz_lightyear.register_factory('string, integer')(factory)
    fuzz_lightyear.register_factory(
        'string, integer',
        operation_ids='get_expect_other_primitives',
    )(other_factory)

    request = FuzzingRequest(
        operation_id='get_expect_primitives',
        tag='types',
    )

    request.send()

    other_request = FuzzingRequest(
        operation_id='get_expect_other_primitives',
        tag='types',
    )

    other_request.send()

    assert request.fuzzed_input['string'] == '1'
    assert request.fuzzed_input['integer'] == 1
    assert other_request.fuzzed_input['string'] == '2'
    assert other_request.fuzzed_input['integer'] == 2


def test_session_fixtures(mock_client):
    count = 0

    def nested_function():
        nonlocal count
        count += 1
        return count

    def child_a(nested):
        return nested

    def child_b(nested):
        return nested

    def function(a, b):
        assert a == b
        return 'does_not_matter'

    fuzz_lightyear.register_factory('nested')(nested_function)
    fuzz_lightyear.register_factory('a')(child_a)
    fuzz_lightyear.register_factory('b')(child_b)
    fuzz_lightyear.register_factory('string')(function)

    request = FuzzingRequest(
        operation_id='get_expect_primitives',
        tag='types',
    )
    request.send()
