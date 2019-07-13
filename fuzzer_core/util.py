from functools import wraps


def cached_result(func):
    """
    This is similar to `lru_cache`, except that it will only store the
    first result, no matter the different inputs the function receives.

    To clear this cache, you can do:
        >>> @cached_result
        ... def foo(**kwargs):
        ...     return 1
        >>> foo.cache_clear()

    This essentially allows for a Singleton class factory. While a bit
    counter-intuitive (since the same inputs to a function should result
    in the same outputs), it allows us to better manage global initialization
    variables, without:
        1. Passing these variables to each function that needs it.
        2. Having a global state that everything can access.

    Rather, this merely attaching global variables to specific functions
    that need it.
    """
    def cache_clear():
        func.__cache__ = None

    func.cache_clear = cache_clear

    @wraps(func)
    def wrapped(*args, **kwargs):
        result = getattr(func, '__cache__', None)
        if result:
            return result

        output = func(*args, **kwargs)
        func.__cache__ = output

        return output

    return wrapped
