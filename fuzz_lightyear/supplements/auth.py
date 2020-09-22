"""
These decorators are used to configure tests for
IDOR (Insecure Direct Object Reference) checks. We need to define two
different accounts (victim and attacker), so that we can check to see
whether the attacker is able to do actions that should only be limited
to the victim.
"""
from typing import Any
from typing import Callable
from typing import Dict

from .abstraction import get_abstraction


def victim_account(
    func: Callable[..., Dict[str, Any]],
) -> Callable[..., Dict[str, Any]]:
    """
    Example Usage:
        >>> @fuzz_lightyear.victim_account
        ... def victim_factory():
        ...     return {
        ...         'headers': {
        ...             'session': 'victim_session_id',
        ...         },
        ...     }

    If operation_id is specified as a parameter in the victim_factory
    then it will be passed in automatically.
    """
    get_abstraction().get_victim_session = func
    return func


def attacker_account(
    func: Callable[..., Dict[str, Any]],
) -> Callable[..., Dict[str, Any]]:
    get_abstraction().get_attacker_session = func
    return func
