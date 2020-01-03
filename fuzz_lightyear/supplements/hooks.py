from typing import Callable
from typing import Iterable
from typing import Optional
from typing import Union

from fuzz_lightyear.datastore import register_post_fuzz_hook
from fuzz_lightyear.util import listify_decorator_args


def post_fuzz(
    operations: Optional[Union[str, Iterable[str]]] = None,
    tags: Optional[Union[str, Iterable[str]]] = None,
    rerun: bool = True,
) -> Callable:

    # These are renamed just to make mypy happy.
    operation_ids = listify_decorator_args(operations)
    _tags = listify_decorator_args(tags)

    def decorator(func: Callable) -> Callable:
        register_post_fuzz_hook(
            hook=func,
            operation_ids=operation_ids,
            tags=_tags,
            rerun=rerun,
        )
        return func

    return decorator
