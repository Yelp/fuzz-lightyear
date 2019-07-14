from typing import List

from .request import FuzzingRequest
from .response import ResponseSequence


def run_sequence(
    sequence: List[FuzzingRequest],
) -> ResponseSequence:
    """
    :raises: bravado.exception.HTTPError
    :raises: bravado_core.exception.SwaggerMappingError
    :raises: jsonschema.exceptions.ValdationError
    """
    result = ResponseSequence()

    # First, determine whether this is a successful request sequence.
    for request in sequence:
        response = request.send()
        result.add_response(response)

    # Then, check for vulnerabilities.
    result.analyze_requests(sequence)
    return result
