from .output.logging import log
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

    def json(self):
        return {
            'tag': self.tag,
            'id': self.operation_id,

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
            auth = get_abstraction().get_victim_session()

        log.info(f'Fuzzing {self.tag}.{self.operation_id}')
        return get_abstraction().request_method(
            operation_id=self.operation_id,
            tag=self.tag,
            *args,
            **auth,
            **self.fuzzed_input,
            **kwargs
        )
