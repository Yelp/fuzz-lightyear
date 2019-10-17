from collections import defaultdict
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import cast
from typing import Dict
from typing import List
from typing import Optional
from urllib.parse import quote_plus
from urllib.parse import urlencode

from bravado.client import CallableOperation
from bravado_core.param import get_param_type_spec      # type: ignore
from cached_property import cached_property             # type: ignore
from hypothesis.searchstrategy.strategies import SearchStrategy

from .fuzzer import fuzz_parameters
from .output.logging import log
from .output.util import print_warning
from .supplements.abstraction import get_abstraction

COLLECTION_FORMAT_CHARS = {
    'csv': ',',
    'tsv': '\t',
    'pipes': '|',
    'ssv': ' ',
}


class FuzzingRequest:
    def __init__(
        self,
        operation_id: str,
        tag: str = 'default',
        **kwargs: Any,
    ) -> None:
        """
        :param operation_id: unique identifier for each Swagger operation.
        :param tag: this is how Swagger operations are grouped.
        """
        self.tag = tag
        self.operation_id = operation_id

        self.fuzzed_input = kwargs              # type: Optional[Dict[str, Any]]
        if not self.fuzzed_input:
            self.fuzzed_input = None

        # This SearchStrategy should be generated with hypothesis' `fixed_dictionaries`,
        # mapping keys to SearchStrategy.
        self._fuzzed_input_factory = None       # type: Optional[SearchStrategy]

    @property
    def id(self) -> str:
        return '{}.{}'.format(
            self.tag,
            self.operation_id,
        )

    def _encode_array_in_path(
        self,
        fuzzed_input: List,
        collection_format: str,
    ) -> str:
        separator = quote_plus(COLLECTION_FORMAT_CHARS[collection_format])
        return separator.join([str(i) for i in fuzzed_input])

    def json(self) -> Dict[str, Any]:
        path = self._swagger_operation.path_name    # type: str
        params = defaultdict(dict)                  # type: Dict[str, Dict[str, Any]]
        if self.fuzzed_input:
            for key, value in self._swagger_operation.params.items():
                if key not in self.fuzzed_input:
                    continue

                if value.location == 'path':
                    if value.param_spec['type'] == 'array':
                        fuzzed_input = self._encode_array_in_path(
                            self.fuzzed_input[key],
                            value.param_spec.get('collectionFormat', 'csv'),
                        )
                    else:
                        fuzzed_input = str(self.fuzzed_input[key])
                    path = path.replace(
                        f'{{{key}}}',
                        fuzzed_input,
                    )
                else:
                    params[value.location][key] = self.fuzzed_input[key]

        return {
            'method': self._swagger_operation.http_method.upper(),
            'path': path,
            **params,
        }

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.tag}.{self.operation_id})'

    def __str__(self) -> str:
        data = self.json()
        url = (
            f'{self._swagger_operation.swagger_spec.api_url.rstrip("/")}'
            f'{data["path"]}'
        )

        if 'query' in data:
            url += '?'
            for key, value in data['query'].items():
                if not isinstance(value, list):
                    # NOTE: value should not be a dict, for a query param.
                    value = [value]
                for v in value:
                    url += f'{key}={quote_plus(str(v).encode())}&'

            url = url.rstrip('&')

        args = []
        if 'formData' in data:
            args.append(f'--data \'{urlencode(data["formData"])}\'')

        if 'header' in data:
            for key, value in data['header'].items():
                args.append(f'-H \'{key}: {value}\'')

        return f'curl -X {data["method"]} {url} {" ".join(args)}'.rstrip()

    def send(
        self,
        auth: Optional[Dict[str, Any]] = None,
        *args: Any,
        should_log: bool = True,
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """
        :param auth: parameters to pass to abstracted request method to specify
            the user making the request.
        :param should_log: this should only be false, if we're sending a
            duplicate request as part of a plugin.
        """
        if not data:
            data = {}

        # Empty dictionary means we're not sending parameters.
        if self.fuzzed_input is None:
            if not self._fuzzed_input_factory:
                parameters = []
                for name, param in self._swagger_operation.params.items():
                    specification = get_param_type_spec(param).copy()
                    if param.location == 'body':
                        # For 'body' parameters, bravado discards information from the
                        # param spec itself. We pass in the 'required' parameter in this
                        # case.
                        # For the 'name' argument (seeing that body parameters can be
                        # named differently), we pass it in separately as it breaks the
                        # swagger specification if we group it together.
                        specification['required'] = param.required

                    parameters.append((name, specification,))

                self._fuzzed_input_factory = fuzz_parameters(parameters)

            # NOTE: If we were really worried about performance later on,
            #       we might be able to address this. Specifically, we don't
            #       *need* to generate examples, just to throw it away later
            #       if the key is already in data.
            #       However, this involves parameter modification, which may
            #       require a more involved change.
            self.fuzzed_input = {}
            for key, value in self._fuzzed_input_factory.example().items():
                if key in data:
                    self.fuzzed_input[key] = data[key]
                    continue

                if value is not None:
                    self.fuzzed_input[key] = value

        if not auth:
            auth = get_victim_session_factory()()

        if should_log:
            log.info(str(self))

        _merge_auth_headers(self.fuzzed_input, auth)

        return get_abstraction().request_method(
            operation_id=self.operation_id,
            tag=self.tag,
            *args,
            **self.fuzzed_input,

            # auth details should override fuzzed_input, because specifics should always
            # override randomly generated content.
            **auth,
            **kwargs
        )

    @cached_property        # type: ignore
    def _swagger_operation(self) -> CallableOperation:
        return cast(
            CallableOperation,
            getattr(
                getattr(get_abstraction().client, self.tag),
                self.operation_id,
            ),
        )


@lru_cache(maxsize=1)
def get_victim_session_factory() -> Callable[..., Dict[str, Any]]:
    factory = get_abstraction().get_victim_session
    if factory:
        return factory

    print_warning('No auth method specified.')
    return lambda: {}


def _merge_auth_headers(fuzzed_params: Dict[str, Any], auth: Dict[str, Any]) -> None:
    """
    The underlying Bravado client allows us to specify request headers on a per-request
    basis (https://bravado.readthedocs.io/en/stable/configuration.html#per-request-configuration).  # noqa: E501
    However, when there are authorization headers specified by the Swagger specification,
    the Bravado library parses it and merges it within the parameters required for the
    callable operation.

    This means, our fuzzing engine will set a value for it, which will override the
    manually specified authorization headers. To address this fact, we replace the fuzzed
    header with the actual one.
    """
    if not auth.get('_request_options', {}).get('headers', None):
        return

    for key in auth['_request_options']['headers']:
        # It looks like Bravado does some serialization for Python purposes, so we need
        # to mirror this.
        key = key.replace('-', '_')
        if key in fuzzed_params:
            fuzzed_params.pop(key)
