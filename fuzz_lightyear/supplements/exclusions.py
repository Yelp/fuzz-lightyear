"""
Not all endpoints which allow a direct object reference needs to be
authenticated. The endpoint could simply be providing non-sensitive information
about the object being queried.

To address this, developers can specify operations which should not be used
in the fuzzing process. We provide two levels of exclusions: non-vulnerable
exclusions and general exclusions.

Non-vulnerable exclusions exclude operations which can be included in the
fuzzing process, but represent a low risk of vulnerabilities, and thus should
not be checked for vulnerabilities for speed of fuzzing and clarity of fuzzing
output.

General exclusions exclude operations which should not be included in the
fuzzing process. Operations that can go here can include operations which don't
function correctly in testing environments.
"""
from functools import wraps
from typing import Callable
from typing import List
from typing import Optional

from fuzz_lightyear.output.util import print_warning


def non_vulnerable_operations() -> Callable:
    """Allows developers to specify operations which
    should not be tested for vulnerabilities.

    Examples:
        Ignoring operations specified by operation ids in lists
            >>> @fuzz_lightyear.exclusions.non_vulnerable_operations
            ... def b():
            ...     return ['get_pets', 'get_store_inventory']
    """
    def decorator(func: Callable) -> Callable:
        wrapped = _get_formatted_operations(func)
        # TODO: do something with this function
        return wrapped

    return decorator


def operations() -> Callable:
    """Allows developers to specify operations which
    should not be called in the fuzzing process.

    Examples:
        Ignoring operations specified by operation ids in lists
            >>> @fuzz_lightyear.exclusions.operations
            ... def b():
            ...     return ['get_pets', 'get_store_inventory']
    """
    def decorator(func: Callable) -> Callable:
        wrapped = _get_formatted_operations(func)
        # TODO: do something with this function
        return wrapped

    return decorator


def _get_formatted_operations(func: Callable) -> Callable[[], List[str]]:
    """
    Given a user-defined function which specifies Swagger operations in a
    supported form,, returns a function `f`. `f()` returns a list
    of Swagger operation id strings.
    """
    @wraps(func)
    def wrapped() -> List[str]:
        operations = func()
        result = []
        for operation in operations:
            formatted_operation = _format_operation(operation)
            if formatted_operation:
                result.append(formatted_operation)

        return result

    return wrapped


def _format_operation(operation) -> Optional[str]:
    if isinstance(operation, str):
        return operation

    print_warning(
        f'Failed to interpret {str(operation)} as an operation to exclude.',
    )
    return None
