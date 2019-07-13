import pytest

from fuzzer_core.client import get_client
from fuzzer_core.datastore import get_user_defined_mapping
from fuzzer_core.supplements.abstraction import get_abstraction


@pytest.fixture(autouse=True)
def clear_caches():
    get_abstraction.cache_clear()
    get_user_defined_mapping.cache_clear()

    get_client.cache_clear()
