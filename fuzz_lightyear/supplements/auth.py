"""
These decorators are used to configure tests for
IDOR (Insecure Direct Object Reference) checks. We need to define two
different accounts (victim and attacker), so that we can check to see
whether the attacker is able to do actions that should only be limited
to the victim.
"""
from ..datastore import inject_user_defined_variables
from .abstraction import get_abstraction


def victim_account(func):
    """
    Example Usage:
        >>> @fuzz_lightyear.victim_account
        ... def victim_factory():
        ...     return {
        ...         'headers': {
        ...             'session': 'victim_session_id',
        ...         },
        ...     }
    """
    get_abstraction().get_victim_session = inject_user_defined_variables(func)
    return func


def attacker_account(func):
    get_abstraction().get_attacker_session = inject_user_defined_variables(func)
    return func
