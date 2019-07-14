"""
NOTE: We can't hardcode any length checks, because this is dependent on a
ever growing test collection. Otherwise, it will make writing tests way more
inconvenient than it needs to be.
"""
from fuzzer_core.generator import generate_sequences


def test_length_one(mock_client):
    results = list(generate_sequences(1))
    for result in results:
        assert len(result.requests) == 1

    assert is_in_result(
        [{
            'tag': 'basic',
            'id': 'get_public_listing',
        }],
        [
            result.requests
            for result in results
        ],
    )


def test_length_three(mock_client):
    """
    We skip length=2 for now, since we only handle all permutations
    for now. length=3 will handle checking for permutations, as well
    as seeing whether failed sequences will be pruned.
    """
    sequences = []
    for result in generate_sequences(3):
        if not result.requests[-1].operation_id.endswith('will_throw_error'):
            result.responses = True

        sequences.append(result.requests)

    for sequence in sequences:
        assert len(sequence) <= 3

        assert not is_in_result(
            [
                {
                    'tag': 'basic',
                    'id': 'get_public_listing',
                },
                {
                    'tag': 'constant',
                    'id': 'get_will_throw_error',
                },
                {
                    'tag': 'basic',
                    'id': 'get_public_listing',
                },
            ],
            sequences,
        )


def is_in_result(expected_sequence, result):
    for sequence in result:
        if [
            request.json()
            for request in sequence
        ] == expected_sequence:
            return True

    return False
