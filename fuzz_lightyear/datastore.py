from functools import lru_cache
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import List


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
        expected_args = _get_injectable_variables(func)

        # Removing metadata, if the function isn't asking for it.
        # This is done *before* injection of user defined factories, so that users
        # can override metadata, if absolutely necessary.
        #
        # Furthermore, metadata is prefixed with `_`, to avoid any potential
        # name collisions with the swagger specification.
        # NOTE: We need to use a local copy, due to our mutation of the iteable.
        for arg_name in list(kwargs.keys()):
            if arg_name.startswith('_') and arg_name not in expected_args:
                kwargs.pop(arg_name)

        for index, arg_name in enumerate(expected_args):
            if index < len(args):
                # This handles the case of explicitly supplied
                # positional arguments, so that we don't pass func
                # two values for the same argument.
                continue

            if arg_name not in kwargs and arg_name in mapping:
                kwargs[arg_name] = mapping[arg_name]()

        return func(*args, **kwargs)

    return wrapped


def _get_injectable_variables(func: Callable) -> List[str]:
    """
    The easiest way to understand this is to see it as an example:

        >>> def func(a, b=1, *args, c, d=2, **kwargs):
        ...     e = 5
        >>>
        >>> print(func.__code__.co_varnames)
        ('a', 'b', 'c', 'd', 'args', 'kwargs', 'e')
        >>> print(func.__code__.co_argcount)    # `a` and `b`
        2
        >>> print(func.__code__.co_kwonlyargcount)  # `c` and `d`
        2
    """
    variable_names = func.__code__.co_varnames
    arg_count = func.__code__.co_argcount + func.__code__.co_kwonlyargcount

    return variable_names[:arg_count]
