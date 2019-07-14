from typing import Iterator
from typing import List

from .client import get_client
from .request import FuzzingRequest
from .result import FuzzingResult


def generate_sequences(n: int) -> Iterator[List[FuzzingResult]]:
    """
    We perform DFS to obtain these sequences, since we want nice output.

    :param n: max length of each sequence.
    """
    client = get_client()
    for tag_group in dir(client):
        last_results = []
        for _ in range(n):
            good_sequences = []
            for sequence in _add_request_to_sequence(tag_group, last_results):
                result = FuzzingResult(sequence)
                yield result

                if result.is_successful():
                    good_sequences.append(sequence)

            last_results = good_sequences


def _add_request_to_sequence(
    tag_group: str,
    seed: List[List[FuzzingRequest]] = None,
) -> List[List[FuzzingRequest]]:
    client = get_client()

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
                #       This means, we need to do all permutations, because we
                #       can't possibly know whether to eagerly prune.
                output.append(new_sequence)

    return output


def _generate_requests(tag_group: str) -> Iterator[FuzzingRequest]:
    """
    Generates all possible requests based on the client's Swagger specification.
    """
    client = get_client()
    for operation_id in dir(getattr(client, tag_group)):
        yield FuzzingRequest(
            operation_id=operation_id,
            tag=tag_group,
        )
