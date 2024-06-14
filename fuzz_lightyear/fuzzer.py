import json
import string
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import hypothesis.provisional as pr
import hypothesis.strategies as st
from hypothesis.strategies import SearchStrategy
from swagger_spec_validator.common import SwaggerValidationError    # type: ignore

from .datastore import get_user_defined_mapping
from .output.logging import log
from .settings import get_settings


def fuzz_parameters(
    parameters: List[Tuple[str, Dict[str, Any]]],
    operation_id: str = None,
) -> SearchStrategy:
    output = {}
    for name, parameter in parameters:
        output[name] = _fuzz_parameter(parameter, operation_id)

    return st.fixed_dictionaries(output)


def _fuzz_parameter(
    parameter: Dict[str, Any],
    operation_id: str = None,
    required: bool = False,
    depth: int = 0,
) -> SearchStrategy:
    """
    :param required: for object types, the required parameter is in a
        separate array, rather than being attached to each parameter
        object. This parameter allows objects to pass in this information.
        e.g. {
            'type': 'object',
            'required': [
                'name',
            ],
            'properties': {
                'name': {
                    'type': 'string',
                },
            },
        }
    """
    required = parameter.get('required', required)

    _type = parameter.get('type')
    if not _type:
        raise SwaggerValidationError(
            'Missing \'type\' from {}'.format(
                json.dumps(parameter),
            ),
        )

    strategy = _get_strategy_from_factory(_type, operation_id, parameter.get('name'))

    if not strategy:
        if 'enum' in parameter:
            return st.sampled_from(parameter['enum'])

        # As per https://swagger.io/docs/specification/data-models/data-types,
        # there are only a limited set of data types.
        mapping = {
            'string': _fuzz_string,
            'number': _fuzz_number,
            'integer': _fuzz_integer,
            'boolean': _fuzz_boolean,
            'array': _fuzz_array,
            'object': _fuzz_object,

            # TODO: handle `file` type
            # https://swagger.io/docs/specification/2-0/file-upload/
        }
        fuzz_fn = mapping[_type]
        if fuzz_fn in (_fuzz_object, _fuzz_array):
            strategy = fuzz_fn(
                parameter,
                operation_id,
                depth + 1,
                required=required,
            )  # type: ignore
        else:
            strategy = fuzz_fn(parameter, required=required)  # type: ignore

    # NOTE: We don't currently support `nullable` values, so we use `None` as a
    #       proxy to exclude the parameter from the final dictionary.
    if (
        # `name` check is used here as a heuristic to determine whether in
        # recursive call (arrays).
        parameter.get('name') and
        not required
    ):
        return st.one_of(st.none(), strategy)  # type: ignore
    return strategy  # type: ignore


def _fuzz_string(
    parameter: Dict[str, Any],
    required: bool = False,
) -> SearchStrategy:
    # TODO: Handle date and date-time string formats.
    # https://swagger.io/docs/specification/data-models/data-types/#string
    if parameter.get('in', None) == 'header':
        return st.text(
            # According to RFC 7230, non-ascii letters are deprecated, and there's
            # no telling what the server will do if they are sent. Since the intent
            # is not to break the server, but to send valid requests instead, we're
            # just going to limit it accordingly.
            alphabet=string.ascii_letters,
        )

    if parameter.get('pattern'):
        full_match = (
            parameter['pattern'][0] == '^'
            and parameter['pattern'][-1] == '$'
            and parameter['pattern'][-2] != '\\'
        )
        return st.from_regex(parameter['pattern'], fullmatch=full_match)

    kwargs = {}                                     # type: Dict[str, Any]

    kwargs['min_size'] = parameter.get('minLength', 0)
    kwargs['max_size'] = parameter.get('maxLength')

    string_format = parameter.get('format')

    if string_format == 'ipv4':
        return pr.ip4_addr_strings()
    elif string_format == 'ipv6':
        return pr.ip6_addr_strings()
    elif string_format == 'binary':
        return st.binary(**kwargs)

    if parameter.get('required', required):
        kwargs['min_size'] = 1

    if not get_settings().unicode_enabled:
        kwargs['alphabet'] = string.printable
    return st.text(**kwargs)


def _find_bounds(schema: Dict[str, Any]) -> Dict[str, Any]:
    """If the schema specifies a maximum and minimum for the numeric value,
       record it.
       By default, maximums and minimums in swagger are not exclusive"""
    bounds = {}
    if 'minimum' in schema:
        bounds['min_value'] = schema['minimum']
        if schema.get('exclusiveMinimum'):
            bounds['min_value'] += 1.0

    if 'maximum' in schema:
        bounds['max_value'] = schema['maximum']
        if schema.get('exclusiveMaximum'):
            bounds['max_value'] -= 1.0
    return bounds


def _fuzz_number(
    parameter: Dict[str, Any],
    **kwargs: Any,
) -> SearchStrategy:
    # TODO: Handle all the optional qualifiers for numbers.
    # https://swagger.io/docs/specification/data-models/data-types/#numbers
    bounds = _find_bounds(parameter)

    return st.floats(**bounds)


def _fuzz_integer(
    parameter: Dict[str, Any],
    **kwargs: Any,
) -> SearchStrategy:
    # TODO: Handle all the optional qualifiers for numbers.
    # https://swagger.io/docs/specification/data-models/data-types/#numbers
    bounds = _find_bounds(parameter)

    return st.integers(**bounds)


def _fuzz_boolean(
    parameter: Dict[str, Any],
    **kwargs: Any,
) -> SearchStrategy:
    return st.booleans()


def _fuzz_array(
    parameter: Dict[str, Any],
    operation_id: str = None,
    depth: int = 0,
    required: bool = False,
) -> SearchStrategy:
    item = parameter['items']
    required = parameter.get('required', required)

    # TODO: Handle `oneOf`
    strategy = st.lists(
        elements=_fuzz_parameter(item, operation_id, required=required, depth=depth + 1),
        min_size=parameter.get(
            'minItems',
            0 if not required else 1,
        ),
        max_size=(0
                  if depth > get_settings().max_fuzz_depth
                  else parameter.get('maxItems', None)),
    )
    if not required:
        return st.one_of(st.none(), strategy)

    return strategy


def _fuzz_object(
    parameter: Dict[str, Any],
    operation_id: str = None,
    depth: int = 0,
    **kwargs: Any,
) -> SearchStrategy:
    # TODO: Handle `additionalProperties`
    output = {}

    if (
        depth > get_settings().max_fuzz_depth or
        'properties' not in parameter
    ):
        return st.none()

    for name, specification in parameter['properties'].items():
        try:
            strategy = _get_strategy_from_factory(
                specification['type'],
                operation_id,
                name,
            )
        except KeyError:
            log.error(
                'Invalid swagger specification: expected \'type\'. Got \'{}\''.format(
                    json.dumps(specification),
                ),
            )
            raise

        if strategy:
            output[name] = strategy
            continue

        # `required` can be True, False, or an array of names that
        # are required.
        required = parameter.get('required', False)
        if required and isinstance(required, list):
            required = name in required

        output[name] = _fuzz_parameter(
            specification,
            operation_id,
            bool(required),
            depth + 1,
        )

    return st.fixed_dictionaries(output)


def _get_strategy_from_factory(
    expected_type: str,
    operation_id: str = None,
    name: Optional[str] = None,
) -> Optional[SearchStrategy[Any]]:
    if name not in get_user_defined_mapping():
        return None

    def type_cast() -> Any:
        """Use known types to cast output, if applicable."""
        if operation_id is None:
            output = get_user_defined_mapping()[name].default_factory()
        else:
            output = get_user_defined_mapping()[name][operation_id]()
        if output is None:
            # NOTE: We don't currently support `nullable` values, so we use `None`
            #       as a proxy to exclude the parameter from the final dictionary.
            return None
        if expected_type == 'string':
            return str(output)
        elif expected_type == 'integer':
            return int(output)

        return output

    return st.builds(type_cast)
