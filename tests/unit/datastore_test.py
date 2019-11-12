import pytest

from fuzz_lightyear.datastore import get_post_fuzz_hooks
from fuzz_lightyear.datastore import register_post_fuzz_hook


class TestPostFuzzHooks:
    @pytest.mark.parametrize(
        ['num_post_fuzz_hooks', 'operation_ids'],
        (
            (1, ['tag1']),
            (1, ['tag1', 'tag2']),
            (2, ['tag1']),
            (2, ['tag1', 'tag2']),
        ),
    )
    def test_registering_hooks_by_operation(self, num_post_fuzz_hooks, operation_ids):
        post_fuzz_hooks = {lambda x, y: y for __ in range(num_post_fuzz_hooks)}

        for hook in post_fuzz_hooks:
            register_post_fuzz_hook(hook, operation_ids=operation_ids)

        for operation_id in operation_ids:
            assert set(get_post_fuzz_hooks(operation_id)) == post_fuzz_hooks

    def test_registering_hooks_all_operations(self):
        def hook(x, y):
            return y
        register_post_fuzz_hook(hook=hook)

        assert set(get_post_fuzz_hooks('random_operation')) == set([hook])
