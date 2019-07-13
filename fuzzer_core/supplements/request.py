from functools import wraps

from .abstraction import get_abstraction


def make_request(func):
    """
    Allows clients to customize how they want to make a request to the
    service undergoing fuzz testing.

    :type func: function
    """
    @wraps(func)
    def wrapped(id_token, *args, **kwargs):
        """
        :type id_token: str
        :param id_token: identifier for authentication/authorization
        """
        return func(id_token=id_token, *args, **kwargs)

    get_abstraction().request_method = wrapped

    return wrapped
