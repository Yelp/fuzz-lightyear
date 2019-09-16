import pytest

import fuzz_lightyear
from fuzz_lightyear.datastore import get_user_defined_mapping
from fuzz_lightyear.exceptions import ConflictingKeys


def test_register_single_key():
    register_function('a', return_value=1)

    mapping = get_user_defined_mapping()
    assert len(mapping) == 1
    assert mapping['a']() == 1


@pytest.mark.parametrize(
    'keys',
    (
        'b, c',
        ['b', 'c'],
    ),
)
def test_register_multiple_keys(keys):
    register_function(keys, return_value=2)

    mapping = get_user_defined_mapping()
    assert len(mapping) == 2
    assert mapping['b']() == 2
    assert mapping['c']() == 2


def test_register_conflicting_key():
    register_function('a')

    with pytest.raises(ConflictingKeys) as e:
        register_function('a')

    assert 'There are multiple factory registrations for "a".' in str(e.value)


def test_basic():
    register_function('a', return_value=1)

    assert get_user_defined_mapping()['a']() == 1


class TestInjectVariables:

    def setup(self):
        fuzz_lightyear.register_factory('nested_dependency')(self.nested_dependency)
        fuzz_lightyear.register_factory('caller')(self.caller)
        fuzz_lightyear.register_factory('dependency')(self.dependency)

    def test_uses_default(self):
        assert get_user_defined_mapping()['caller']() == 2

    def test_throws_error_when_no_default(self):
        def foobar(no_default):
            pass
        fuzz_lightyear.register_factory('a')(foobar)

        with pytest.raises(TypeError):
            get_user_defined_mapping()['a']()

    def test_nested_dependency(self):
        assert get_user_defined_mapping()['nested_dependency']() == 4

    def test_re_registration(self):
        function = fuzz_lightyear.register_factory('a')(self.dependency)
        fuzz_lightyear.register_factory('b')(function)

        assert get_user_defined_mapping()['b']() == 1

    @staticmethod
    def nested_dependency(caller):
        return caller * 2

    @staticmethod
    def caller(dependency):
        return dependency + 1

    @staticmethod
    def dependency():
        return 1


def _custom_type(value):
    """Used for TestTypeHinting."""
    return value + 2


class TestTypeHinting:
    """Root level type casting is done in integration tests."""

    def setup(self):
        fuzz_lightyear.register_factory('dependency')(self.dependency)
        fuzz_lightyear.register_factory('string_factory')(self.string_factory)
        fuzz_lightyear.register_factory('integer_factory')(self.integer_factory)
        fuzz_lightyear.register_factory('custom_factory')(self.custom_factory)

    def test_type_hinting_for_nested_dependencies(self):
        assert get_user_defined_mapping()['string_factory']() == 'test_string'
        assert get_user_defined_mapping()['integer_factory']() == 2

    def test_custom_type(self):
        assert get_user_defined_mapping()['custom_factory']() == 3

    @staticmethod
    def dependency():
        return 1

    @staticmethod
    def string_factory(dependency: str):
        assert dependency == '1'
        return 'test_string'

    @staticmethod
    def integer_factory(dependency: int):
        assert dependency == 1
        return 2

    @staticmethod
    def custom_factory(dependency: _custom_type):
        return dependency


def register_function(key, return_value=None):
    def foobar():
        return return_value

    fuzz_lightyear.register_factory(key)(foobar)
    return foobar
