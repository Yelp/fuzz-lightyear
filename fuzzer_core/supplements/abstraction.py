from functools import lru_cache
from typing import Callable

from fuzzer_core.client import get_client
from fuzzer_core.exceptions import ConflictingHandlers


@lru_cache(maxsize=1)
def get_abstraction():
    return Abstraction()


class Abstraction:
    """
    Allows clients to configure various parts of the fuzzer's core functionality,
    all exposed through one single interface.
    """

    def __init__(self):
        self.get_victim_session = None      # type: Callable
        self.get_attacker_session = None    # type: Callable

        self._request_method = None         # type: Callable

    @property
    def request_method(self):
        if self._request_method:
            return self._request_method

        return default_request_method

    @request_method.setter
    def request_method(self, func):
        """
        :type func: function
        """
        if self._request_method:
            raise ConflictingHandlers('make_request')

        self._request_method = func


def default_request_method(operation_id, tag='default', *args, **kwargs):
    """
    :type operation_id: str
    :param operation_id: there's a unique operationId for each
        (tag, operation) in the Swagger schema

    :type tag: str
    :param tag: Swagger tag
    """
    future = getattr(getattr(get_client(), tag), operation_id)(*args, **kwargs)
    return future.result()
