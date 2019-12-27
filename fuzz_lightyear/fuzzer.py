import json
import string
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import hypothesis.strategies as st
from hypothesis.strategies import SearchStrategy
from swagger_spec_validator.common import SwaggerValidationError    # type: ignore

from .datastore import get_user_defined_mapping
from .output.logging import log
from .settings import get_settings


def fuzz_parameters(
    parameters: List[Tuple[str, Dict[str, Any]]],
) -> SearchStrategy:
    output = {}
    for name, parameter in parameters:
        output[name] = _fuzz_parameter(parameter)

    return st.fixed_dictionaries(output)


def _fuzz_parameter(
    parameter: Dict[str, Any],
    required: bool = False,
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

    strategy = _get_strategy_from_factory(_type, parameter.get('name'))

    if not strategy:
        if 'enum' in parameter:
            return st.sampled_from(parameter['enum'])

        # As per https://swagger.io/docs/specification/data-models/data-types,
        # there are only a limited set of data types.
        mapping = {     # type: ignore # mypy doesn't like dynamic function signatures
            'string': _fuzz_string,
            'number': _fuzz_number,
            'integer': _fuzz_integer,
            'boolean': _fuzz_boolean,
            'array': _fuzz_array,
            'object': _fuzz_object,

            # TODO: handle `file` type
            # https://swagger.io/docs/specification/2-0/file-upload/
        }
        strategy = mapping[_type](parameter, required=required)

    # NOTE: We don't currently support `nullable` values, so we use `None` as a
    #       proxy to exclude the parameter from the final dictionary.
    if (
        # `name` check is used here as a heuristic to determine whether in
        # recursive call (arrays).
        parameter.get('name')
        and not required
    ):
        return st.one_of(st.none(), strategy)
    return strategy


def _fuzz_string(
    parameter: Dict[str, Any],
    required: bool = False,
) -> SearchStrategy:
    if parameter.get('in', None) == 'header':
        return st.text(
            # According to RFC 7230, non-ascii letters are deprecated, and there's
            # no telling what the server will do if they are sent. Since the intent
            # is not to break the server, but to send valid requests instead, we're
            # just going to limit it accordingly.
            alphabet=string.ascii_letters,
        )

    # TODO: Handle a bunch of swagger string formats.
    # https://swagger.io/docs/specification/data-models/data-types/#string
    kwargs = {}                                     # type: Dict[str, Any]

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
            bounds['min_vallue'] += 1.0

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
    required: bool = False,
) -> SearchStrategy:
    item = parameter['items']
    required = parameter.get('required', required)

    # TODO: Handle `oneOf`
    strategy = st.lists(
        elements=_fuzz_parameter(item, required=required),
        min_size=parameter.get(
            'minItems',
            0 if not required else 1,
        ),
        max_size=parameter.get('maxItems', None),
    )
    if not required:
        return st.one_of(st.none(), strategy)

    return strategy


def _fuzz_object(
    parameter: Dict[str, Any],
    **kwargs: Any,
) -> SearchStrategy:
    # TODO: Handle `additionalProperties`
    output = {}
    for name, specification in parameter['properties'].items():
        try:
            strategy = _get_strategy_from_factory(specification['type'], name)
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
            bool(required),
        )

    return st.fixed_dictionaries(output)


def _get_strategy_from_factory(
    expected_type: str,
    name: Optional[str] = None,
) -> Optional[SearchStrategy[Any]]:
    if name not in get_user_defined_mapping():
        return None

    def type_cast() -> Any:
        """Use known types to cast output, if applicable."""
        output = get_user_defined_mapping()[name]()
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
