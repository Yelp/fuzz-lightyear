import json
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import hypothesis.strategies as st
from hypothesis.searchstrategy.strategies import SearchStrategy
from swagger_spec_validator.common import SwaggerValidationError    # type: ignore

from .datastore import get_user_defined_mapping
from .supplements.abstraction import get_abstraction


def fuzz_parameters(
    parameters: List[Tuple[str, Dict[str, Any]]],
) -> SearchStrategy:
    output = {}
    for name, parameter in parameters:
        parameter = _deref(parameter)

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
    parameter = _deref(parameter)
    required = parameter.get('required', required)
    strategy = None

    if 'enum' in parameter:
        strategy = st.sampled_from(parameter['enum'])

    _type = parameter.get('type')
    if not _type:
        raise SwaggerValidationError(
            'Missing \'type\' from {}'.format(
                json.dumps(parameter),
            ),
        )

    if (
        # Since this is recursively called, this qualifier needs to be
        # here to support array definitions.
        not strategy and
        parameter.get('name') and
        parameter['name'] in get_user_defined_mapping()
    ):
        strategy = st.builds(
            get_user_defined_mapping()[parameter['name']],
        )

    if not strategy:
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
        parameter.get('name') and
        not required
    ):
        return st.one_of(st.none(), strategy)
    return strategy


def _fuzz_string(
    parameter: Dict[str, Any],
    required: bool = False,
) -> SearchStrategy:
    # TODO: Handle a bunch of swagger string formats.
    # https://swagger.io/docs/specification/data-models/data-types/#string
    if parameter.get('required', required):
        return st.text(min_size=1)

    return st.text()


def _fuzz_number(
    parameter: Dict[str, Any],
    **kwargs
) -> SearchStrategy:
    # TODO: Handle all the optional qualifiers for numbers.
    # https://swagger.io/docs/specification/data-models/data-types/#numbers
    return st.floats()


def _fuzz_integer(
    parameter: Dict[str, Any],
    **kwargs
) -> SearchStrategy:
    # TODO: Handle all the optional qualifiers for numbers.
    # https://swagger.io/docs/specification/data-models/data-types/#numbers
    return st.integers()


def _fuzz_boolean(
    parameter: Dict[str, Any],
    **kwargs
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
    **kwargs
) -> SearchStrategy:
    # TODO: Handle `additionalProperties`
    return st.fixed_dictionaries({
        name: _fuzz_parameter(
            specification,
            name in parameter.get('required', []),
        )
        for name, specification in parameter['properties'].items()
    })


def _deref(parameter: Dict[str, Any]) -> Dict[str, Any]:
    while '$ref' in parameter:
        parameter = _get_model_definition(parameter['$ref'])

    return parameter


def _get_model_definition(
    reference: str,
) -> Dict[str, Any]:
    """
    :param reference: e.g. '#/defintions/{ModelName}'
    """
    # TODO: Handle multiple files?
    try:
        model_name = reference.split('/')[-1]
        return get_abstraction().client.swagger_spec.definitions[model_name]._model_spec
    except (IndexError, KeyError):  # pragma: no cover
        raise SwaggerValidationError(f'Failed to get model: {reference}')
