from fuzzer_core.util import cached_result


def test_cached_result():
    @cached_result
    def foobar(**kwargs):
        return kwargs

    assert foobar(foo='bar') == {'foo': 'bar'}
    assert foobar() == {'foo': 'bar'}

    foobar.cache_clear()
    assert foobar() == {}
