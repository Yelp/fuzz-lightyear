from functools import lru_cache
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict


@lru_cache(maxsize=1)
def get_user_defined_mapping() -> Dict:
    """
    This is essentially a global variable, within a function scope, because
    this returns a reference to the cached dictionary.

    :rtype: dict(str => function)
    """
    return {}


def inject_user_defined_variables(func: Callable) -> Callable:
    """
    This decorator allows the use of user defined variables in functions.
    e.g.
        >>> @fuzz_lightyear.register_factory('name')
        ... def name():
        ...     return 'freddy'
        >>>
        >>> @inject_user_defined_variables
        ... def foobar(name):
        ...     print(name)     # freddy
    """
    mapping = get_user_defined_mapping()

    @wraps(func)
    def wrapped(*args, **kwargs) -> Any:
        for arg_name in func.__code__.co_varnames[len(args):]:
            if arg_name not in kwargs and arg_name in mapping:
                kwargs[arg_name] = mapping[arg_name]()

        return func(*args, **kwargs)

    return wrapped
