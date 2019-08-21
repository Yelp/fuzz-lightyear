from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple

from .request import FuzzingRequest
from .result import FuzzingResult
from .supplements.abstraction import get_abstraction


def generate_sequences(
    n: int,
    tests: Optional[Tuple[str, ...]] = None,
) -> Iterator[FuzzingResult]:
    """
    We perform DFS to obtain these sequences, since we want nice output.

    :param n: max length of each sequence.
    :param tests: specifies the tests we want to run.
    """
    # TODO: It would probably better if we can sort on ending operation
    #       (rather than starting operation), so that it's clearer for
    #       output.
    client = get_abstraction().client
    for tag_group in dir(client):
        last_results = []   # type: List
        for _ in range(n):
            good_sequences = []
            for sequence in _add_request_to_sequence(tag_group, last_results):
                # TODO: We can probably modify this algorithm to be better.
                if (
                    tests and not
                    (
                        sequence[-1].id in tests or
                        sequence[-1].tag in tests
                    )
                ):
                    continue

                result = FuzzingResult(sequence)
                yield result

                if result.is_successful():
                    good_sequences.append(sequence)

            last_results = good_sequences


def _add_request_to_sequence(
    tag_group: str,
    seed: Optional[List[List[FuzzingRequest]]] = None,
) -> List[List[FuzzingRequest]]:
    client = get_abstraction().client

    if not seed:
        return [
            [request]
            for request in _generate_requests(tag_group)
        ]

    output = []
    for sequence in seed:
        for tag_group in dir(client):
            for request in _generate_requests(tag_group):
                # Attempt to add every single permutation first.
                new_sequence = sequence + [request]

                # TODO: sequence pruning. We would get a lot better results if
                #       we only added a request that consumes resources that
                #       have been created by the sequence so far. However, due
                #       to the nature of microservices, we may need to rely on
                #       factories for this.
                #
                #       This is further made complicated because we have no idea
                #       whether a request should consume an existing resource,
                #       use a factory, or fuzz a value.
                #
                #       This means, we need to do all permutations, because we
                #       can't possibly know whether to eagerly prune.
                output.append(new_sequence)

    return output


def _generate_requests(tag_group: str) -> Iterator[FuzzingRequest]:
    """
    Generates all possible requests based on the client's Swagger specification.
    """
    client = get_abstraction().client
    for operation_id in dir(getattr(client, tag_group)):
        yield FuzzingRequest(
            operation_id=operation_id,
            tag=tag_group,
        )
