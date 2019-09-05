import pytest

import fuzz_lightyear
from fuzz_lightyear.supplements.exclusions import get_excluded_operations


@pytest.mark.parametrize(
    'excluded_operations_input, expected_exclusions',
    [
        (
            ['get_pets'],
            {'get_pets': None},
        ),
        (
            ['get_pets', 'get_store_inventory'],
            {'get_pets': None, 'get_store_inventory': None},
        ),
        (
            ['pets.get_pets'],
            {'get_pets': 'pets'},
        ),
        (
            ['pets.get_pets', 'store.get_store_inventory'],
            {'get_pets': 'pets', 'get_store_inventory': 'store'},
        ),
    ],
)
def test_exclude_operations_strings(
    excluded_operations_input,
    expected_exclusions,
):
    def foobar():
        return excluded_operations_input

    fuzz_lightyear.exclusions.operations()(foobar)
    assert get_excluded_operations() == expected_exclusions
