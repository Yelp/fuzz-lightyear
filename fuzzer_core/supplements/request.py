from .abstraction import get_abstraction


def make_request(func):
    """
    Allows clients to customize how they want to make a request to the
    service undergoing fuzz testing.

    :type func: function
    """
    get_abstraction().request_method = func
    return func
