from functools import lru_cache

from .output.logging import log
from .output.util import print_warning
from .supplements.abstraction import get_abstraction


class FuzzingRequest:
    def __init__(self, operation_id, tag='default', **kwargs):
        """
        :type operation_id: str
        :param operation_id: unique identifier for each Swagger operation.

        :type tag: str
        :param tag: this is how Swagger operations are grouped.
        """
        self.tag = tag
        self.operation_id = operation_id

        self.fuzzed_input = kwargs

    @property
    def id(self):
        return '{}.{}'.format(
            self.tag,
            self.operation_id,
        )

    def json(self):
        return {
            **self.fuzzed_input,
        }

    def send(self, auth=None, *args, **kwargs):
        """
        :type auth: dict
        :param auth: parameters to pass to abstracted request method to specify
            the user making the request.
        """
        # TODO: fuzz parameters
        if not auth:
            auth = get_victim_session_factory()()

        log.info(f'Fuzzing {self.id}')
        return get_abstraction().request_method(
            operation_id=self.operation_id,
            tag=self.tag,
            *args,
            **auth,
            **self.fuzzed_input,
            **kwargs
        )


@lru_cache(maxsize=1)
def get_victim_session_factory():
    factory = get_abstraction().get_victim_session
    if factory:
        return factory

    print_warning('No auth method specified.')
    return lambda: {}
