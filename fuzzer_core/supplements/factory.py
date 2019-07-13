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
from functools import wraps

from fuzzer_core.datastore import get_user_defined_mapping
from fuzzer_core.exceptions import ConflictingKeys


def register_factory(keys):
    """
    :type keys: str|iterable

    Basic Use:
        >>> import fuzzer_core
        >>> @fuzzer_core.register_factory('user_id')
        ... def create_user():
        ...     return 1

    Multiple Keys:
        >>> @fuzzer_core.register_factory(['biz_id', 'business_id'])
        ... def create_business():
        ...     return 1
        >>>
        >>> @fuzzer_core.register_factory('biz_id, business_id')
        ... def create_business():
        ...     return 1

    Dependency Injection:
        >>> @fuzzer_core.register_factory('biz_id')
        ... def create_business():
        ...     return 1
        >>>
        >>> @fuzzer_core.register_factory('biz_user_id')
        ... def create_biz_user(biz_id):
        ...     return 2
    """
    if isinstance(keys, str):
        keys = [
            key.strip()
            for key in keys.split(',')
        ]

    def decorator(func):
        mapping = get_user_defined_mapping()

        @wraps(func)
        def wrapped(*args, **kwargs):
            for arg_name in func.__code__.co_varnames[len(args):]:
                if arg_name not in kwargs and arg_name in mapping:
                    kwargs[arg_name] = mapping[arg_name]()

            return func(*args, **kwargs)

        for key in keys:
            if key in mapping:
                raise ConflictingKeys(key)

            mapping[key] = wrapped

        return wrapped

    return decorator
