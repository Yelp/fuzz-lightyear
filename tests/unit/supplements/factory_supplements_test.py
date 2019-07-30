import pytest

import fuzz_lightyear
from fuzz_lightyear.datastore import get_user_defined_mapping
from fuzz_lightyear.datastore import inject_user_defined_variables
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
        fuzz_lightyear.register_factory('const_num')(self.returns_two)

    def test_uses_default(self):
        assert get_user_defined_mapping()['caller']() == 2

    def test_uses_provided_value_over_default(self):
        # assert get_user_defined_mapping()['caller'](dependency=2) == 3
        assert get_user_defined_mapping()['caller'](3) == 4

    def test_throws_error_when_no_default(self):
        def foobar(no_default):
            pass
        fuzz_lightyear.register_factory('a')(foobar)

        with pytest.raises(TypeError):
            get_user_defined_mapping()['a']()

    def test_nested_dependency(self):
        assert get_user_defined_mapping()['nested_dependency']() == 4

    def test_decorator_compatibility(self):
        def decorator(func):
            def wrapped(*args, const_num, **kwargs):
                output = inject_user_defined_variables(func)(*args, **kwargs)

                return output + const_num

            return wrapped

        fuzz_lightyear.register_factory('decorator')(decorator(self.caller))

        assert get_user_defined_mapping()['decorator']() == 1 + 1 + 2

    @staticmethod
    def nested_dependency(caller):
        return caller * 2

    @staticmethod
    def caller(dependency):
        return dependency + 1

    @staticmethod
    def dependency():
        return 1

    @staticmethod
    def returns_two():
        return 2


def register_function(key, return_value=None):
    def foobar():
        return return_value

    fuzz_lightyear.register_factory(key)(foobar)
    return foobar
