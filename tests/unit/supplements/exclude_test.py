import pytest

import fuzz_lightyear
from fuzz_lightyear.datastore import get_excluded_operations
from fuzz_lightyear.datastore import get_non_vulnerable_operations


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
        (
            [None],
            {},
        ),
        (
            ['get_pets', None],
            {'get_pets': None},
        ),
    ],
)
@pytest.mark.parametrize(
    'exclusions_decorator, get_exclusions_function',
    [
        (
            fuzz_lightyear.exclude.operations,
            get_excluded_operations,
        ),
        (
            fuzz_lightyear.exclude.non_vulnerable_operations,
            get_non_vulnerable_operations,
        ),
    ],
)
def test_exclude_operations_strings(
    excluded_operations_input,
    expected_exclusions,
    exclusions_decorator,
    get_exclusions_function,
):
    def foobar():
        return excluded_operations_input

    exclusions_decorator(foobar)
    assert get_exclusions_function() == expected_exclusions
