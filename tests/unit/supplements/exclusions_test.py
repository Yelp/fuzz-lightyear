import pytest

import fuzz_lightyear


@pytest.mark.parametrize(
    'excluded_operations',
    [
        (['get_pets']),
        (['get_pets', 'get_store_inventory']),
        (['pets.get_pets']),
        (['pets.get_pets', 'store.get_store_inventory']),
    ],
)
def test_exclude_operations_strings(excluded_operations):
    def foobar():
        return excluded_operations

    fuzz_lightyear.exclusions.operations()(foobar)

    # Just make sure the above didn't raise an exception for now
    # TODO: test the decoration's side-effect once it has a side-effect
