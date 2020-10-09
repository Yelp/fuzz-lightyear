"""
Due to a micro-service ecosystem, services' swagger files may not come
with complete CRUD (Create-Retrieve-Update-Delete) functionality. This
makes it difficult to test since we lack the resource IDs necessary to
determine whether there are vulnerabilities in the retrieve/update/delete
functions.

In order to address this issue, we need to supplement our tests with
an ability to create adhoc resources directly. These functions support this,
and allow developers to configure their tests as necessary.
"""
from collections import defaultdict
from typing import Callable
from typing import Iterable
from typing import Union

from fuzz_lightyear.datastore import get_user_defined_mapping
from fuzz_lightyear.datastore import inject_user_defined_variables
from fuzz_lightyear.exceptions import ConflictingKeys
from fuzz_lightyear.util import listify_decorator_args


def register_factory(
    keys: Union[str, Iterable[str]],
    *,
    operation_ids: Union[str, Iterable[str]] = None,
) -> Callable:
    """
    :type keys: str|iterable
    :type operation_ids: str|iterable

    Basic Use:
        >>> import fuzz_lightyear
        >>> @fuzz_lightyear.register_factory('user_id')
        ... def create_user():
        ...     return 1

    Multiple Keys:
        >>> @fuzz_lightyear.register_factory(['biz_id', 'business_id'])
        ... def create_business():
        ...     return 1
        >>>
        >>> @fuzz_lightyear.register_factory('biz_id, business_id')
        ... def create_business():
        ...     return 1

    Endpoint Specific:
        >>> @fuzz_lightyear.register_factory('biz_id', operation_ids='test_operation')
        ... def create_test_business():
        ...     return 2

    Dependency Injection:
        >>> @fuzz_lightyear.register_factory('biz_id')
        ... def create_business():
        ...     return 1
        >>>
        >>> @fuzz_lightyear.register_factory('biz_user_id')
        ... def create_biz_user(biz_id):
        ...     assert biz_id == 1
        ...     return 2

    Type Hinting:
        This is free for root level factories, using the expected type based
        on the swagger specification. For transitive use of factories, we
        employ type-casting through type hints.

        I'm aware that this means Python 3 will be required (and may not be
        easy to implement for legacy codebases) but this is the easiest way
        to implement this (without essentially implementing it ourselves).

        For more edge cases and considerations, check out the test cases.

        >>> @fuzz_lightyear.register_factory('biz_id')
        ... def create_business():
        ...     return 3
        >>>
        >>> @fuzz_lightyear.register_factory('biz_user_id')
        ... def create_biz_user(biz_id: str):
        ...     assert biz_id == '3'
        ...     return 4
    """
    # This is renamed just to make mypy happy.
    _keys = listify_decorator_args(keys)
    _operation_ids = listify_decorator_args(operation_ids)

    def decorator(func: Callable) -> Callable:

        wrapped = inject_user_defined_variables(func, )

        mapping = get_user_defined_mapping()
        for key in _keys:
            if key not in mapping:
                if _operation_ids:
                    mapping[key] = defaultdict(lambda: returns_none)
                    for operation_id in _operation_ids:
                        mapping[key][operation_id] = inject_user_defined_variables(
                            func,
                            operation_id=operation_id,
                        )
                else:
                    # Make defaultdict with wrapped as default
                    mapping[key] = defaultdict(lambda: wrapped)
            else:
                func_dict = mapping[key]
                if _operation_ids:
                    for operation_id in _operation_ids:
                        if operation_id in func_dict:
                            raise ConflictingKeys(key, operation_id)
                        else:
                            func_dict[operation_id] = inject_user_defined_variables(
                                func,
                                operation_id=operation_id,
                            )
                else:
                    if func_dict.default_factory() == returns_none:
                        func_dict.default_factory = lambda: wrapped
                    else:
                        # We don't want to set a conflicting default
                        raise ConflictingKeys(key)

        return wrapped

    return decorator


def returns_none() -> None:
    return None
