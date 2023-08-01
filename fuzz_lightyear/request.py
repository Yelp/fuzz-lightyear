import inspect
import json
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
from hypothesis.strategies import SearchStrategy  # noqa: F401

from .datastore import get_post_fuzz_hooks
from .datastore import inject_user_defined_variables
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

        if 'body' in data:
            # NOTE: The first `body` key specifies where it's found.
            #       The second specifies the object that was fuzzed.
            #       Since there's only *one* body parameter (with a variable
            #       name), we can parse it out as such.
            args.append(f'--data \'{json.dumps(list(data["body"].values())[0])}\'')
            data['header'] = data.get('header', {})
            data['header']['Content-Type'] = 'application/json'

        # NOTE: We default to using the victim's auth headers, assuming that
        # this function is primarily used for easy reproduction (in which,
        # it should not matter the specific session that we use).
        headers = data.get('header', {})

        victim_headers_func = get_victim_session_factory()
        victim_headers = _get_auth_header(victim_headers_func, self.operation_id)
        headers.update(
            victim_headers.get(
                '_request_options', {},
            ).get(
                'headers', {},
            ),
        )
        for key, value in headers.items():
            args.append(f'-H \'{key}: {value}\'')

        return f'curl -X {data["method"]} {url} {" ".join(args)}'.rstrip()

    def send(
        self,
        auth: Optional[Callable[..., Dict[str, Any]]] = None,
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
            self.fuzzed_input = self.fuzz(data)
            self.apply_post_fuzz_hooks(self.fuzzed_input, rerun=False)
        else:
            # On the first run, self.fuzzed_input will be initialized
            # to a dictionary. Therefore, if this request is sent again,
            # this code path will execute, and we will want to rerun
            # the applicable post_fuzz hooks.
            #
            # TODO: I wonder whether we have to distinguish between
            # explicitly initialized `fuzzed_input`, and *actually* fuzzed
            # input, given that the former case will technically be the
            # *first* time the post_fuzz hook is run.
            self.apply_post_fuzz_hooks(self.fuzzed_input, rerun=True)

        if not auth:
            auth = get_victim_session_factory()
        auth_header = _get_auth_header(auth, self.operation_id)

        if should_log:
            log.info(str(self))

        _merge_auth_headers(self.fuzzed_input, auth_header)

        # auth details should override fuzzed_input, because
        # specifics should always override randomly generated content
        kwargs = _merge_kwargs(self.fuzzed_input, auth_header, kwargs)

        return get_abstraction().request_method(
            operation_id=self.operation_id,
            tag=self.tag,
            *args,
            **kwargs,
        )

    def fuzz(self, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Returns a dictionary of values which can be used
        to call the operation being fuzzed.
        """
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

            self._fuzzed_input_factory = fuzz_parameters(parameters, self.operation_id)

        # NOTE: If we were really worried about performance later on,
        #       we might be able to address this. Specifically, we don't
        #       *need* to generate examples, just to throw it away later
        #       if the key is already in data.
        #       However, this involves parameter modification, which may
        #       require a more involved change.
        fuzzed_input = {}
        for key, value in self._fuzzed_input_factory.example().items():
            if key in existing_data:
                fuzzed_input[key] = existing_data[key]
                continue

            if value is not None:
                fuzzed_input[key] = value

        return fuzzed_input

    def apply_post_fuzz_hooks(
        self,
        fuzzed_input: Dict[str, Any],
        rerun: Optional[bool] = False,
    ) -> None:
        """After parameters for a request are fuzzed, this function
        applies developer-supplied post-fuzz hooks to the fuzzed
        input.

        :param fuzzed_input: The initial fuzz result from `self.fuzz`.
        """
        hooks = get_post_fuzz_hooks(self.operation_id, self.tag, rerun)
        for hook in hooks:
            hook(
                self._swagger_operation,
                fuzzed_input,
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
    return inject_user_defined_variables(lambda: {})


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


def _merge_kwargs(*args: Any) -> Dict[str, Any]:
    """Merges the input dictionaries into a single dictionary which
    can be used in a fuzzing request.

    We need to merge headers and request_options seperately since
    they themselves are dictionaries.
    """

    headers = {}  # type: Dict[str, str]
    for dictionary in args:
        headers.update(dictionary.get('_request_options', {}).get('headers', {}))

    request_options = {}  # type: Dict[str, Any]
    for dictionary in args:
        # NOTE: this code does not merge the Bravado
        # response_callbacks option correctly, but we don't use it
        # in fuzz-lightyear. _request_options docs:
        # https://bravado.readthedocs.io/en/stable/configuration.html
        request_options.update(dictionary.get('_request_options', {}))

    output = {}  # type: Dict[str, Any]
    for dictionary in args:
        output.update(dictionary)

    output['_request_options'] = request_options
    output['_request_options']['headers'] = headers

    return output


def _get_auth_header(func: Callable[..., Dict[str, Any]], op_id: str) -> Dict[str, Any]:
    header_args = inspect.getfullargspec(func.__wrapped__)  # type: ignore
    if 'operation_id' in header_args.args:
        auth_header = func(op_id)
    else:
        auth_header = func()
    return auth_header
