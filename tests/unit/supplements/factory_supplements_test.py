import pytest

import fuzz_lightyear
from fuzz_lightyear.datastore import get_user_defined_mapping
from fuzz_lightyear.exceptions import ConflictingKeys


def test_register_single_key():
    register_function('a', return_value=1)

    mapping = get_user_defined_mapping()
    assert len(mapping) == 1
    assert mapping['a']['opid']() == 1


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
    assert mapping['b']['opid']() == 2
    assert mapping['c']['opid']() == 2


def test_register_conflicting_key():
    register_function('a')

    with pytest.raises(ConflictingKeys) as e:
        register_function('a')

    assert 'There are multiple factory registrations for "a".' in str(e.value)


def test_basic():
    register_function('a', return_value=1)

    assert get_user_defined_mapping()['a']['opid']() == 1


class TestEndpointFixtures:
    """
    Note: Since defaultdict creates a key-value pair once a non-existent key
    is called, if we change the default value, keys that have been encountered
    will not have the new value. This shouldn't be a problem since we don't
    do not request keys until all the factories are registered.
    """

    def test_register_endpoints_default(self):
        register_function('a', return_value=1)

        assert get_user_defined_mapping()['a']['endpoint']() == 1
        assert get_user_defined_mapping()['a']['other_endpoint']() == 1

    def test_register_endpoints_no_default(self):
        register_function('a', operation_ids=['endpoint'], return_value=1)

        assert get_user_defined_mapping()['a']['endpoint']() == 1
        assert get_user_defined_mapping()['a']['other_endpoint']() is None

    def test_register_endpoints_both(self):
        register_function('a', return_value=1)
        register_function('a', operation_ids=['other_endpoint'], return_value=2)

        assert get_user_defined_mapping()['a']['endpoint']() == 1
        assert get_user_defined_mapping()['a']['other_endpoint']() == 2


class TestInjectVariables:

    def setup(self):
        fuzz_lightyear.register_factory('nested_dependency')(self.nested_dependency)
        fuzz_lightyear.register_factory('caller')(self.caller)
        fuzz_lightyear.register_factory(
            'caller',
            operation_ids='new_opid',
        )(self.special_caller)
        fuzz_lightyear.register_factory(
            'caller',
            operation_ids='only_opid',
        )(self.endpt_specific_caller)
        fuzz_lightyear.register_factory('dependency')(self.dependency)
        fuzz_lightyear.register_factory(
            'endpt_dependency',
            operation_ids='only_opid',
        )(self.dependency)

    def test_uses_default(self):
        assert get_user_defined_mapping()['caller']['opid']() == 2

    def test_nested_endpoint_dependency(self):
        assert get_user_defined_mapping()['caller']['new_opid']() == 3

    def test_throws_error_when_no_default(self):
        def foobar(no_default):
            pass
        fuzz_lightyear.register_factory('a')(foobar)

        with pytest.raises(TypeError):
            get_user_defined_mapping()['a']['opid']()

    def test_nested_dependency(self):
        assert get_user_defined_mapping()['nested_dependency']['opid']() == 4

    # We resolve operation_id-specific dependencies if the current
    # factory is specified for the same operation id.
    def test_endpoint_dependency_single(self):
        get_user_defined_mapping()['caller']['only_opid']() == 3

    @pytest.mark.xfail(reason='See https://github.com/Yelp/fuzz-lightyear/issues/62')
    def test_nested_generic_dependency_uses_specific_dependency(self):
        assert get_user_defined_mapping()['nested_dependency']['new_opid']() == 6

    def test_re_registration(self):
        function = fuzz_lightyear.register_factory('a')(self.dependency)
        fuzz_lightyear.register_factory('b')(function)

        assert get_user_defined_mapping()['b']['opid']() == 1

    @staticmethod
    def nested_dependency(caller):
        return caller * 2

    @staticmethod
    def caller(dependency):
        return dependency + 1

    @staticmethod
    def special_caller(dependency):
        return dependency + 2

    @staticmethod
    def endpt_specific_caller(endpt_dependency):
        return endpt_dependency + 2

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
        assert get_user_defined_mapping()['string_factory']['opid']() == 'test_string'
        assert get_user_defined_mapping()['integer_factory']['opid']() == 2

    def test_custom_type(self):
        assert get_user_defined_mapping()['custom_factory']['opid']() == 3

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


def register_function(key, operation_ids=None, return_value=None):
    def foobar():
        return return_value

    fuzz_lightyear.register_factory(key, operation_ids=operation_ids)(foobar)
    return foobar
