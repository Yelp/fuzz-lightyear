import pytest

from fuzz_lightyear.datastore import get_post_fuzz_hooks
from fuzz_lightyear.datastore import register_post_fuzz_hook


class TestPostFuzzHooks:
    @pytest.mark.parametrize(
        'num_post_fuzz_hooks',
        [1, 2],
    )
    @pytest.mark.parametrize(
        'operation_ids',
        [
            ['tag1'],
            ['tag1, tag2'],
        ],
    )
    @pytest.mark.parametrize(
        'rerun',
        [True, False],
    )
    def test_registering_hooks_by_operation(
        self,
        num_post_fuzz_hooks,
        operation_ids,
        rerun,
    ):
        post_fuzz_hooks = {lambda x, y: y for __ in range(num_post_fuzz_hooks)}

        for hook in post_fuzz_hooks:
            register_post_fuzz_hook(hook, operation_ids=operation_ids, rerun=rerun)

        for operation_id in operation_ids:
            assert set(get_post_fuzz_hooks(operation_id, rerun=rerun)) == post_fuzz_hooks

    def test_registering_hooks_all_operations(self):
        def hook(x, y):
            return y
        register_post_fuzz_hook(hook=hook)

        assert set(get_post_fuzz_hooks('random_operation')) == set([hook])
