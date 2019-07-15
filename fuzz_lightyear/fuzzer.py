import json
from typing import Any
from typing import Dict
from typing import List

import hypothesis.strategies as st
from hypothesis.searchstrategy.strategies import SearchStrategy
from swagger_spec_validator.common import SwaggerValidationError    # type: ignore

from .client import get_client
from .datastore import get_user_defined_mapping


def fuzz_parameters(
    parameters: List[Dict[str, Any]],
) -> SearchStrategy:
    return st.fixed_dictionaries({
        parameter['name']: _fuzz_parameter(parameter)
        for parameter in parameters
    })


def _fuzz_parameter(
    parameter: Dict[str, Any],
) -> SearchStrategy:
    if '$ref' in parameter:
        parameter = _get_model_definition(parameter['$ref'])

    if 'enum' in parameter:
        return st.sampled_from(parameter['enum'])

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
        parameter.get('name') and
        parameter['name'] in get_user_defined_mapping()
    ):
        return st.builds(
            get_user_defined_mapping()[parameter['name']],
        )

    # As per https://swagger.io/docs/specification/data-models/data-types,
    # there are only a limited set of data types.
    mapping = {
        'string': _fuzz_string,
        'number': _fuzz_number,
        'integer': _fuzz_integer,
        'boolean': _fuzz_boolean,
        'array': _fuzz_array,
        'object': _fuzz_object,
    }
    strategy = mapping[_type](parameter)

    # NOTE: We don't currently support `nullable` values, so we use `None` as a
    #       proxy to exclude the parameter from the final dictionary.
    if (
        # `name` check is used here as a heuristic to determine whether in
        # recursive call (arrays).
        parameter.get('name') and
        not parameter.get('required', False)
    ):
        return st.one_of(st.none(), strategy)
    return strategy


def _fuzz_string(
    parameter: Dict[str, Any],
) -> SearchStrategy:
    # TODO: Handle a bunch of swagger string formats.
    # https://swagger.io/docs/specification/data-models/data-types/#string
    if parameter.get('required', False):
        return st.text(min_size=1)

    return st.text()


def _fuzz_number(
    parameter: Dict[str, Any],
) -> SearchStrategy:
    # TODO: Handle all the optional qualifiers for numbers.
    # https://swagger.io/docs/specification/data-models/data-types/#numbers
    return st.floats()


def _fuzz_integer(
    parameter: Dict[str, Any],
) -> SearchStrategy:
    # TODO: Handle all the optional qualifiers for numbers.
    # https://swagger.io/docs/specification/data-models/data-types/#numbers
    return st.integers()


def _fuzz_boolean(
    parameter: Dict[str, Any],
) -> SearchStrategy:
    return st.booleans()


def _fuzz_array(
    parameter: Dict[str, Any],
) -> SearchStrategy:
    item = parameter['items']

    # TODO: Handle `oneOf`
    strategy = st.lists(
        elements=_fuzz_parameter(item),
        min_size=parameter.get('minItems', 0),
        max_size=parameter.get('maxItems', None),
    )
    if not parameter.get('required', False):
        return st.one_of(st.none(), strategy)

    return strategy


def _fuzz_object(
    parameter: Dict[str, Any],
) -> SearchStrategy:
    # TODO: Handle `additionalProperties`
    return st.fixed_dictionaries({
        name: _fuzz_parameter(specification)
        for name, specification in parameter['properties'].items()
    })


def _get_model_definition(
    reference: str,
) -> Dict[str, Any]:
    """
    :param reference: e.g. '#/defintions/{ModelName}'
    """
    # TODO: Handle multiple files?
    try:
        model_name = reference.split('/')[-1]
        return get_client().swagger_spec.definitions[model_name]._model_spec
    except (IndexError, KeyError):  # pragma: no cover
        raise SwaggerValidationError(f'Failed to get model: {reference}')
