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
