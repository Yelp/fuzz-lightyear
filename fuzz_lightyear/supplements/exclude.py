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
from typing import Dict
from typing import Optional
from typing import Tuple

from fuzz_lightyear.datastore import get_excluded_operations
from fuzz_lightyear.datastore import get_non_vulnerable_operations
from fuzz_lightyear.output.util import print_warning


def non_vulnerable_operations(func: Callable) -> Callable:
    """Allows developers to specify operations which
    should not be tested for vulnerabilities.

    Examples:
        Ignoring operations specified by operation ids in lists
            >>> @fuzz_lightyear.exclude.non_vulnerable_operations
            ... def b():
            ...     return ['get_pets', 'get_store_inventory']

        Ignoring operations specified by "tag.operation_id" in lists
            >>> @fuzz_lightyear.exclude.non_vulnerable_operations
            ... def c():
                    return ['pets.get_pets', 'store.get_store_inventory']
    """
    get_operations_fn = _get_formatted_operations(func)
    get_non_vulnerable_operations().update(get_operations_fn())

    return func


def operations(func: Callable) -> Callable:
    """Allows developers to specify operations which
    should not be called in the fuzzing process.

    Examples:
        Ignoring operations specified by operation ids in lists
            >>> @fuzz_lightyear.exclude.operations
            ... def b():
            ...     return ['get_pets', 'get_store_inventory']

        Ignoring operations specified by "tag.operation_id" in lists
            >>> @fuzz_lightyear.exclude.operations
            ... def c():
            ...     return ['pets.get_pets', 'store.get_store_inventory']
    """
    get_operations_fn = _get_formatted_operations(func)
    get_excluded_operations().update(get_operations_fn())

    return func


def _get_formatted_operations(func: Callable) -> Callable[[], Dict[str, Optional[str]]]:
    """
    Given a user-defined function which specifies Swagger operations in a
    supported form,, returns a function `f`. `f()` returns a mapping
    from swagger operation id to its tag.
    """
    @wraps(func)
    def wrapped() -> Dict[str, Optional[str]]:
        operations = func()
        result = {}
        for operation in operations:
            formatted_operation = _format_operation(operation)
            if formatted_operation:
                operation_id, tag = formatted_operation
                result[operation_id] = tag

        return result

    return wrapped


def _format_operation(operation: str) -> Optional[Tuple[str, Optional[str]]]:
    if isinstance(operation, str):
        num_dots = operation.count('.')
        if num_dots == 0:
            return (operation, None)
        elif num_dots == 1:
            tag, operation_id = operation.split('.')
            return (operation_id, tag)

    print_warning(
        f'Failed to interpret {str(operation)} as an operation to exclude.',
    )
    return None
