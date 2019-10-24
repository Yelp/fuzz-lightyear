from typing import Callable

from fuzz_lightyear.datastore import get_setup_fixtures


def setup(func: Callable) -> Callable:
    """
    Use the @setup decorator to mark functions that you'd like execute prior
    to running fuzz-lightyear tests

    Decorated functions should be in the file along with your factory fixtures

    Basic use:

        >>> import fuzz lightyear
        >>> @fuzz_lightyear.setup
        ... def setup_config():
        ...     // do configuration here

    """
    setup_fixtures = get_setup_fixtures()
    setup_fixtures.append(func)
    return func
