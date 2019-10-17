from typing import Callable
from typing import Iterable

from fuzz_lightyear.datastore import get_included_tags


def tags(func: Callable[[], Iterable[str]]) -> Callable:
    """Allows developers to specify Swagger tags which
    should be fuzzed.

    Example:
        Only fuzz operations with the 'user_account' tag.
            >>> @fuzz_lightyear.include.tags
            ... def a():
            ...     return ['user_account']
    """
    tags_to_include = func()
    if tags_to_include:
        get_included_tags().update(tags_to_include)

    return func
