import inspect
from functools import lru_cache
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


@lru_cache(maxsize=1)
def get_user_defined_mapping() -> Dict:
    """
    This is essentially a global variable, within a function scope, because
    this returns a reference to the cached dictionary.

    :rtype: dict(str => function)
    """
    return {}


@lru_cache(maxsize=1)
def get_excluded_operations() -> Dict[str, Optional[str]]:
    """
    This is a global dictionary containing fuzzing-excluded operations.
    Operation id's are keys. Tags are values, if the user provided them.
    If you don't care about the operation's tag, you can get just the
    excluded operations with `get_excluded_operations().keys()`.

    :rtype: dict(str => str)
    """
    return {}


@lru_cache(maxsize=1)
def get_non_vulnerable_operations() -> Dict[str, Optional[str]]:
    """
    This is a global dictionary containing non-vulnerable operations.
    Operation ids are keys. Tags are values, if the user provided them.
    If you don't care about the operation's tag, you can get just the
    excluded operations with `get_excluded_operations().keys()`.

    :rtype: dict(str => str)
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
        type_annotations = inspect.getfullargspec(func).annotations

        for index, arg_name in enumerate(expected_args):
            if index < len(args):
                # This handles the case of explicitly supplied
                # positional arguments, so that we don't pass func
                # two values for the same argument.
                continue

            if arg_name not in kwargs and arg_name in mapping:
                value = mapping[arg_name]()
                if (
                    arg_name in type_annotations and
                    not isinstance(type_annotations[arg_name], type(List))
                ):
                    # If type annotations are used, use that to cast
                    # values for input.
                    value = type_annotations[arg_name](value)

                kwargs[arg_name] = value

        return func(*args, **kwargs)

    return wrapped


def _get_injectable_variables(func: Callable) -> Tuple[str, ...]:
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
