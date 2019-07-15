from collections import defaultdict
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Dict
from urllib.parse import urlencode

from bravado.client import CallableOperation
from bravado_core.param import get_param_type_spec      # type: ignore
from cached_property import cached_property             # type: ignore
from hypothesis.searchstrategy.strategies import SearchStrategy

from .client import get_client
from .fuzzer import fuzz_parameters
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

        self.fuzzed_input = kwargs              # type: Dict[str, Any]
        if not self.fuzzed_input:
            self.fuzzed_input = None

        self._fuzzed_input_factory = None       # type: Dict[str, SearchStrategy]

    @property
    def id(self) -> str:
        return '{}.{}'.format(
            self.tag,
            self.operation_id,
        )

    def json(self) -> Dict[str, Any]:
        path = self._swagger_operation.path_name    # type: str
        params = defaultdict(dict)                  # type: Dict[str, Dict[str, Any]]
        if self.fuzzed_input:
            for key, value in self._swagger_operation.params.items():
                if key not in self.fuzzed_input:
                    continue

                if value.location == 'path':
                    path = path.replace(f'{{{key}}}', self.fuzzed_input[key])
                else:
                    params[value.location][key] = self.fuzzed_input[key]

        return {
            'method': self._swagger_operation.http_method.upper(),
            'path': path,
            **params,
        }

    def __repr__(self):
        return f'{self.__class__.__name__}({self.tag}.{self.operation_id})'

    def __str__(self):
        data = self.json()
        url = (
            f'{self._swagger_operation.swagger_spec.api_url.rstrip("/")}'
            f'{data["path"]}'
        )

        if 'query' in data:
            url += f'?{urlencode(data["query"])}'

        args = []
        if 'formData' in data:
            args.append(f'--data \'{urlencode(data["formData"])}\'')

        if 'header' in data:
            for key, value in data['header'].items():
                args.append(f'-H \'{key}: {value}\'')

        return f'curl -X {data["method"]} {url} {" ".join(args)}'.rstrip()

    def send(self, auth=None, *args, **kwargs) -> Any:
        """
        :type auth: dict
        :param auth: parameters to pass to abstracted request method to specify
            the user making the request.
        """
        # Empty dictionary means we're not sending parameters.
        if self.fuzzed_input is None:
            if not self._fuzzed_input_factory:
                parameters = [
                    get_param_type_spec(param)
                    for param in self._swagger_operation.params.values()
                ]

                self._fuzzed_input_factory = fuzz_parameters(parameters)

            self.fuzzed_input = {
                key: value
                for key, value in self._fuzzed_input_factory.example().items()
                if value
            }

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

    @cached_property
    def _swagger_operation(self) -> CallableOperation:
        return getattr(
            getattr(get_client(), self.tag),
            self.operation_id,
        )


@lru_cache(maxsize=1)
def get_victim_session_factory() -> Callable:
    factory = get_abstraction().get_victim_session
    if factory:
        return factory

    print_warning('No auth method specified.')
    return lambda: {}
