import pytest

from fuzz_lightyear.client import get_client
from fuzz_lightyear.datastore import get_user_defined_mapping
from fuzz_lightyear.plugins import get_enabled_plugins
from fuzz_lightyear.request import get_victim_session_factory
from fuzz_lightyear.supplements.abstraction import get_abstraction


@pytest.fixture(autouse=True)
def clear_caches():
    get_abstraction.cache_clear()
    get_user_defined_mapping.cache_clear()
    get_enabled_plugins.cache_clear()
    get_victim_session_factory.cache_clear()

    get_client.cache_clear()
