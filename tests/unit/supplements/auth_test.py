import pytest

import fuzz_lightyear
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
    def generator():
        return 1
    fuzz_lightyear.register_factory('user_id')(generator)

    def wrapped(user_id):
        assert user_id == 1
    getattr(auth, function)(wrapped)

    getattr(get_abstraction(), f'get_{function.replace("account", "session")}')()
