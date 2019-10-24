import pytest

import fuzz_lightyear
from fuzz_lightyear.datastore import get_included_tags


@pytest.mark.parametrize(
    'included_tags, expected_result',
    [
        (
            ['tag1', 'tag2'],
            {'tag1', 'tag2'},
        ),
        (
            set(['tag1', 'tag2']),
            {'tag1', 'tag2'},
        ),
        (
            [],
            set(),
        ),
    ],
)
def test_include_tags(included_tags, expected_result):
    def foobar():
        return included_tags

    fuzz_lightyear.include.tags(foobar)
    assert get_included_tags() == expected_result
