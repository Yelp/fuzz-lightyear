from functools import lru_cache


@lru_cache(maxsize=1)
def get_user_defined_mapping():
    """
    This is essentially a global variable, within a function scope, because
    this returns a reference to the cached dictionary.

    :rtype: dict(str => function)
    """
    return {}
