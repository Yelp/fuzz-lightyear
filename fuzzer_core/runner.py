from typing import List

from bravado.exception import HTTPError
from bravado_core.exception import SwaggerMappingError
from jsonschema.exceptions import ValidationError

from .request import FuzzingRequest
from .response import ResponseSequence


def run_sequence(
    sequence: List[FuzzingRequest],
) -> ResponseSequence:
    """
    :returns: if False, request sequence was not successful.
    """
    result = ResponseSequence()

    # First, determine whether this is a successful request sequence.
    for request in sequence:
        try:
            response = request.send()
        except (HTTPError, SwaggerMappingError, ValidationError):
            return

        result.responses.append(response)

    # Then, check for vulnerabilities.
    result.analyze_requests(sequence)
    return result
