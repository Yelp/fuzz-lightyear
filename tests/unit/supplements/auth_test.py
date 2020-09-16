import pytest

from fuzz_lightyear.supplements import auth
from fuzz_lightyear.supplements.abstraction import get_abstraction


@pytest.mark.parametrize(
    'function',
    (
        'victim_account',
        'attacker_account',
    ),
)
def test_inject_variables(function):
    def session_headers(operation_id):
        assert operation_id == 'test_operation'
    getattr(auth, function)(session_headers)

    getattr(
        get_abstraction(),
        f'get_{function.replace("account", "session")}',
    )('test_operation')


@pytest.mark.parametrize(
    'function',
    (
        'victim_account',
        'attacker_account',
    ),
)
def test_no_variables(function):
    def session_headers():
        return True
    getattr(auth, function)(session_headers)

    getattr(get_abstraction(), f'get_{function.replace("account", "session")}')()
