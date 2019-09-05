"""
NOTE: We can't hardcode any length checks, because this is dependent on a
ever growing test collection. Otherwise, it will make writing tests way more
inconvenient than it needs to be.
"""
import pytest

import fuzz_lightyear
from fuzz_lightyear.generator import generate_sequences


@pytest.fixture
def excluded_operations(request):
    if not isinstance(request.param, list):
        raise ValueError

    def get_exclusions():
        return request.param

    fuzz_lightyear.exclusions.operations()(get_exclusions)
    yield
    fuzz_lightyear.exclusions.operations()(lambda: {})


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


@pytest.mark.parametrize(
    'excluded_operations',
    [
        (['constant.get_will_throw_error']),
        (['get_will_throw_error']),
    ],
    indirect=['excluded_operations'],
)
def test_exclude_operations(mock_client, excluded_operations):
    results = list(generate_sequences(1))
    assert not is_in_result(
        [{
            'tag': 'constant',
            'id': 'get_will_throw_error',
        }],
        [
            result.requests
            for result in results
        ],
    )


def test_supply_single_test(mock_client):
    results = list(generate_sequences(1, ['basic.get_public_listing']))
    assert len(results) == 1


def test_supply_multiple_tests(mock_client):
    results = list(
        generate_sequences(
            1,
            [
                'basic.get_public_listing',
                'basic.get_private_listing',
            ],
        ),
    )
    assert len(results) == 2


def test_supply_class_of_tests(mock_client):
    results = list(generate_sequences(1, ['basic']))
    for result in results:
        assert result.requests[0].tag == 'basic'


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
        formatted_sequence = []
        for request in sequence:
            formatted_sequence.append({
                'tag': request.tag,
                'id': request.operation_id,
            })

        if formatted_sequence == expected_sequence:
            return True

    return False
