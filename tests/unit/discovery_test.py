import os

import pytest

from fuzz_lightyear import discovery
from fuzz_lightyear.supplements.abstraction import get_abstraction


class TestImportFixture:

    def test_file(self):
        discovery.import_fixtures(
            get_path('../../test_data/nested/directory/fixtures.py'),
        )

        assert get_abstraction().get_victim_session
        assert not get_abstraction().get_attacker_session

    @pytest.mark.parametrize(
        'path',
        (
            '../../test_data/nested/directory',
            '../../test_data/nested/directory/',
        ),
    )
    def test_directory(self, path):
        discovery.import_fixtures(get_path(path))

        assert get_abstraction().get_victim_session
        assert not get_abstraction().get_attacker_session

    def test_nested_directory(self):
        discovery.import_fixtures(
            get_path('../../test_data/nested'),
        )

        assert get_abstraction().get_victim_session
        assert get_abstraction().get_attacker_session


def test_import_module_from_path():
    module = discovery.import_module_from_path(
        get_path('../../test_data/module.py'),
    )
    assert module.this_returns_one() == 1


def get_path(path):
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            path,
        ),
    )
