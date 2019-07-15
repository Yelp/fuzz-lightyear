import pytest

import fuzz_lightyear
from fuzz_lightyear.exceptions import ConflictingHandlers
from fuzz_lightyear.supplements.abstraction import get_abstraction


def test_basic():
    def request_handler(operation_id):
        assert operation_id == 'status'

    fuzz_lightyear.make_request(request_handler)
    get_abstraction().request_method(
        'status',
    )


def test_passes_other_arguments():
    def request_handler(operation_id, *args, **kwargs):
        assert kwargs['headers']['session'] == 'id_token'

    fuzz_lightyear.make_request(request_handler)
    get_abstraction().request_method(
        'status',
        headers={
            'session': 'id_token',
        },
    )


def test_throws_error_if_multiple_handlers():
    def request_handler_one(*args):
        pass

    def request_handler_two(*args):
        pass

    fuzz_lightyear.make_request(request_handler_one)
    with pytest.raises(ConflictingHandlers):
        fuzz_lightyear.make_request(request_handler_two)
