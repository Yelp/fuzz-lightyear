from functools import lru_cache

from fuzzer_core.exceptions import ConflictingHandlers
from fuzzer_core.exceptions import MissingRequiredConfiguration


@lru_cache(maxsize=1)
def get_abstraction():
    return Abstraction()


class Abstraction:
    """
    Allows clients to configure various parts of the fuzzer's core functionality,
    all exposed through one single interface.
    """

    def __init__(self):
        self._request_method = None

    @property
    def request_method(self):
        if self._request_method:
            return self._request_method

        raise MissingRequiredConfiguration(
            'Missing configuration for request handling! Please use '
            '`@fuzzer_core.make_request` to define this handler.',
        )

    @request_method.setter
    def request_method(self, func):
        """
        :type func: function
        """
        if self._request_method:
            raise ConflictingHandlers('make_request')

        self._request_method = func
