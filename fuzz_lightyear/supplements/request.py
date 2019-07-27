from typing import Callable

from .abstraction import get_abstraction


def make_request(func: Callable) -> Callable:
    """
    Allows clients to customize how they want to make a request to the
    service undergoing fuzz testing.
    """
    get_abstraction().request_method = func
    return func


def custom_swagger_client(func: Callable) -> None:
    """
    Allows client to customize a SwaggerClient, so that they can leverage
    the default request handler.
    """
    get_abstraction().client = func()
