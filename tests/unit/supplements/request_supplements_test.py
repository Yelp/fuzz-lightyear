import pytest

import fuzz_lightyear
from fuzz_lightyear.exceptions import ConflictingHandlers
from fuzz_lightyear.supplements.abstraction import get_abstraction


class TestMakeRequest:
    def test_basic(self):
        def request_handler(operation_id):
            assert operation_id == 'status'

        fuzz_lightyear.make_request(request_handler)
        get_abstraction().request_method(
            'status',
        )

    def test_passes_other_arguments(self):
        def request_handler(operation_id, *args, **kwargs):
            assert kwargs['headers']['session'] == 'id_token'

        fuzz_lightyear.make_request(request_handler)
        get_abstraction().request_method(
            'status',
            headers={
                'session': 'id_token',
            },
        )

    def test_throws_error_if_multiple_handlers(self):
        def request_handler_one(*args):
            pass

        def request_handler_two(*args):
            pass

        fuzz_lightyear.make_request(request_handler_one)
        with pytest.raises(ConflictingHandlers):
            fuzz_lightyear.make_request(request_handler_two)


def test_custom_swagger_client():
    def declaration():
        return 1

    fuzz_lightyear.custom_swagger_client(declaration)
    assert get_abstraction().client == 1
