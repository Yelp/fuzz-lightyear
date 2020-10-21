from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from .datastore import clear_cache
from .datastore import get_user_defined_mapping
from .request import FuzzingRequest
from .response import ResponseSequence


def validate_sequence(
    sequence: List[FuzzingRequest],
    responses: ResponseSequence,
) -> ResponseSequence:

    run_sequence(sequence, responses)
    # Then, check for vulnerabilities.
    responses.analyze_requests(sequence)
    clear_cache()
    return responses


def run_sequence(
    sequence: List[FuzzingRequest],
    responses: ResponseSequence,
    auth: Optional[Callable[..., Dict[str, Any]]] = None,
) -> ResponseSequence:

    # First, determine whether this is a successful request sequence.
    for request in sequence:
        response = request.send(
            data=responses.data,
            auth=auth,
        )

        responses.add_response(response)

        # The Response object already saves the output of the response.
        # However, we also still want to save some of the *inputs* to the
        # request, if they were factory-generated. This tries to ensure
        # the same object is referenced throughout the sequence, rather than
        # having the fuzzing engine constantly generate new objects.
        for key in request.fuzzed_input:                            # type: ignore
            if key in get_user_defined_mapping():
                if get_user_defined_mapping()[key][request.operation_id]() is not None:
                    responses.data[key] = request.fuzzed_input[key]     # type: ignore
    return responses
