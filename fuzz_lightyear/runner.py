from typing import List

from .request import FuzzingRequest
from .response import ResponseSequence


def run_sequence(
    sequence: List[FuzzingRequest],
    responses: ResponseSequence,
):
    # First, determine whether this is a successful request sequence.
    for request in sequence:
        response = request.send()
        responses.add_response(response)

    # Then, check for vulnerabilities.
    responses.analyze_requests(sequence)
    return responses
