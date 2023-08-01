from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Optional  # noqa: F401

from bravado.client import SwaggerClient  # noqa: F401

from fuzz_lightyear.exceptions import ConflictingHandlers


class Abstraction:
    """
    Allows clients to configure various parts of the fuzzer's core functionality,
    all exposed through one single interface.
    """

    def __init__(self) -> None:
        self.get_victim_session = None      # type: Optional[Callable]
        self.get_attacker_session = None    # type: Optional[Callable]

        self.client = None                  # type: Optional[SwaggerClient]
        self._request_method = None         # type: Optional[Callable]

    @property
    def request_method(self) -> Callable:
        if self._request_method:
            return self._request_method

        return default_request_method

    @request_method.setter
    def request_method(self, func: Callable) -> None:
        if self._request_method:
            raise ConflictingHandlers('make_request')

        self._request_method = func


@lru_cache(maxsize=1)
def get_abstraction() -> Abstraction:
    return Abstraction()


def default_request_method(
    operation_id: str,
    tag: str = 'default',
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    :param operation_id: there's a unique operationId for each
        (tag, operation) in the Swagger schema

    :param tag: Swagger tag
    """
    future = getattr(
        getattr(get_abstraction().client, tag),
        operation_id,
    )(*args, **kwargs)
    return future.result()
