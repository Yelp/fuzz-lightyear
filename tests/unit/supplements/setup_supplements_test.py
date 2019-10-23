import fuzz_lightyear
from fuzz_lightyear.main import run_user_defined_setup


def test_setup():
    count = 40

    def setup_function():
        nonlocal count
        count = 50

    fuzz_lightyear.setup(setup_function)
    run_user_defined_setup()

    assert count == 50
