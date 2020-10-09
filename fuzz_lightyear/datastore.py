import inspect
from collections import defaultdict
from functools import lru_cache
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from bravado.client import CallableOperation


PostFuzzHook = Callable[[CallableOperation, Dict[str, Any]], None]


# These are module variables which contain the post-fuzz hooks
# which have been registered. Each global allows fuzz_lightyear
# to get a list applicable to a certain operation or tag.
_ALL_POST_FUZZ_HOOKS_BY_OPERATION = defaultdict(set)  # type: Dict[str, Set[PostFuzzHook]]
_ALL_POST_FUZZ_HOOKS_BY_TAG = defaultdict(set)  # type: Dict[str, Set[PostFuzzHook]]

# This probably isn't scalable if we add more parameters to
# hooks , but for now this works, and is easy to understand.
_RERUN_POST_FUZZ_HOOKS_BY_OPERATION = defaultdict(set)  # type: Dict[str, Set[PostFuzzHook]]  # noqa: E501
_RERUN_POST_FUZZ_HOOKS_BY_TAG = defaultdict(set)  # type: Dict[str, Set[PostFuzzHook]]


def register_post_fuzz_hook(
    hook: PostFuzzHook,
    operation_ids: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    rerun: bool = True,
) -> None:
    """Adds a post-fuzz hook to fuzz_lightyear's store of post-fuzz
    hooks.

    :param hook: The hook.
    :param operation_ids: A list of operations that the input hook
    applies to.
    :param tags: A list of Swagger tags that the input hook applies
    to.
    :param rerun: Whether this hook needs to be rerun if a request
    is rerun (for example, in the idor plugin).
    """
    if not operation_ids and not tags:
        operation_ids = ['*']

    if not operation_ids:
        operation_ids = []

    if not tags:
        tags = []

    for operation_id in operation_ids:
        _ALL_POST_FUZZ_HOOKS_BY_OPERATION[operation_id].add(hook)
        if rerun:
            _RERUN_POST_FUZZ_HOOKS_BY_OPERATION[operation_id].add(hook)

    for tag in tags:
        _ALL_POST_FUZZ_HOOKS_BY_TAG[tag].add(hook)
        if rerun:
            _RERUN_POST_FUZZ_HOOKS_BY_TAG[tag].add(hook)


def get_post_fuzz_hooks(
    operation_id: str,
    tag: Optional[str] = None,
    rerun: Optional[bool] = False,
) -> List[PostFuzzHook]:
    """Returns a list of functions that should be applied to fuzzed
    data for the input operation.
    """
    operation_hook_store = _RERUN_POST_FUZZ_HOOKS_BY_OPERATION \
        if rerun \
        else _ALL_POST_FUZZ_HOOKS_BY_OPERATION

    tag_hook_store = _RERUN_POST_FUZZ_HOOKS_BY_TAG \
        if rerun \
        else _ALL_POST_FUZZ_HOOKS_BY_TAG

    operation_hooks = operation_hook_store[operation_id].union(
        operation_hook_store['*'],
    )
    tag_hooks = tag_hook_store[tag] if tag else set()
    return list(operation_hooks.union(tag_hooks))


@lru_cache(maxsize=1)
def get_setup_fixtures() -> List:
    """
    This is a global list that contains the functions that should be executed
    before fuzz-lightyear begins executing tests.

    :rtype: list(function)
    """
    return []


@lru_cache(maxsize=1)
def get_user_defined_mapping() -> Dict:
    """
    This is essentially a global variable, within a function scope, because
    this returns a reference to the cached dictionary. The mapping is a
    dictionary with variable names as keys. The values are defaultdicts
    mapping endpoints to fuzzing factories. If a default value does not
    exist, then the default value will be None.

    :rtype: dict(str => defaultdict(str => function))
    :returns: mapping from variable_name => operation_id => user_defined_function
    """
    return {}


@lru_cache(maxsize=1)
def get_included_tags() -> Set[str]:
    """This is a global set containing tags which should
    be fuzzed. Each element is a string for the tag which
    should be included.
    """
    return set()


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


def clear_cache() -> None:
    """ Clear the cached values for fixture functions """
    for operation_ids in get_user_defined_mapping().values():
        for value in operation_ids.values():
            value._fuzz_cache = None


def inject_user_defined_variables(
        original_callable: Callable = None,
        *,
        operation_id: str = None
) -> Callable:
    """
    This decorator allows the use of user defined variables in functions.
    By default it uses default_factory for the values, but if an operation_id
    is passed in we use that to determine the value instead.
    e.g.
        >>> @fuzz_lightyear.register_factory('name')
        ... def name():
        ...     return 'freddy'
        >>>
        >>> @inject_user_defined_variables
        ... def foobar(name):
        ...     print(name)     # freddy
        >>>
        >>> @fuzz_lightyear.register_factory('name', operation_ids='foo')
        ... def name():
        ...     return 'nathan'
        >>>
        >>> @inject_user_defined_variables(operation_id='foo')
        ... def foobar(name):
        ...     print(name)     # nathan
    """
    def inject_variables(func: Callable) -> Callable:
        mapping = get_user_defined_mapping()

        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            arg_tuple = (args, tuple(sorted(kwargs)))
            if getattr(func, '_fuzz_cache', None) is not None \
                    and arg_tuple in func._fuzz_cache:  # type: ignore
                return func._fuzz_cache[arg_tuple]  # type: ignore

            expected_args = _get_injectable_variables(func)
            type_annotations = inspect.getfullargspec(func).annotations

            for index, arg_name in enumerate(expected_args):
                if index < len(args):
                    # This handles the case of explicitly supplied
                    # positional arguments, so that we don't pass func
                    # two values for the same argument.
                    continue

                if arg_name not in mapping:
                    raise TypeError
                if operation_id is not None:
                    value = mapping[arg_name][operation_id]()

                else:
                    from .supplements.factory import returns_none
                    fixture_func = mapping[arg_name].default_factory()
                    if fixture_func == returns_none:
                        raise TypeError
                    value = fixture_func()
                if (
                    arg_name in type_annotations
                    and not isinstance(type_annotations[arg_name], type(List))
                ):
                    # If type annotations are used, use that to cast
                    # values for input.
                    value = type_annotations[arg_name](value)

                kwargs[arg_name] = value

            if getattr(func, '_fuzz_cache', None) is not None:
                func._fuzz_cache[arg_tuple] = func(*args, **kwargs)  # type: ignore
            else:
                func._fuzz_cache = {arg_tuple: func(*args, **kwargs)}  # type: ignore
            return func._fuzz_cache[arg_tuple]  # type: ignore

        return wrapped
    if original_callable and callable(original_callable):
        return inject_variables(original_callable)
    else:
        return inject_variables


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
