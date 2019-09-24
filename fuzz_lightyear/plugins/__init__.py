from functools import lru_cache
from typing import Sequence
from typing import Type

from ..output.logging import log
from ..supplements.abstraction import get_abstraction
from .base import BasePlugin
from .idor import IDORPlugin


@lru_cache(maxsize=1)
def get_enabled_plugins() -> Sequence[Type[BasePlugin]]:
    plugins = []

    if (
        get_abstraction().get_victim_session and
        get_abstraction().get_attacker_session
    ):
        plugins.append(IDORPlugin)

    if not plugins:
        log.warning(
            'No plugins enabled! Be sure to check your configurations.',
        )

    return plugins
