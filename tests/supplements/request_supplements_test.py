import pytest

import fuzzer_core
from fuzzer_core.exceptions import ConflictingHandlers
from fuzzer_core.exceptions import MissingRequiredConfiguration
from fuzzer_core.supplements.abstraction import get_abstraction


def test_basic():
    def request_handler(id_token):
        assert id_token == id_token

    fuzzer_core.make_request(request_handler)
    get_abstraction().request_method(
        'id_token',
    )


def test_passes_other_arguments():
    def request_handler(*args, **kwargs):
        assert kwargs['headers']['session'] == 'id_token'

    fuzzer_core.make_request(request_handler)
    get_abstraction().request_method(
        'id_token',
        headers={
            'session': 'id_token',
        },
    )


def test_throws_error_if_no_handler():
    with pytest.raises(MissingRequiredConfiguration):
        get_abstraction().request_method('a')


def test_throws_error_if_multiple_handlers():
    def request_handler_one(*args):
        pass

    def request_handler_two(*args):
        pass

    fuzzer_core.make_request(request_handler_one)
    with pytest.raises(ConflictingHandlers):
        fuzzer_core.make_request(request_handler_two)
