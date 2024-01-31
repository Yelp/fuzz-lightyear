import random
from functools import lru_cache

from hypothesis import core

from fuzz_lightyear.config import ENABLE_COLOR
from fuzz_lightyear.config import MAX_FUZZ_DEPTH
from fuzz_lightyear.config import SEED_RANDOM_LENGTH
from fuzz_lightyear.config import UNICODE_ENABLED


class Settings:
    def __init__(self) -> None:
        self.seed = random.getrandbits(SEED_RANDOM_LENGTH)  # type: int
        self.unicode_enabled = UNICODE_ENABLED              # type: bool
        self.enable_color = ENABLE_COLOR                    # type: bool
        self.max_fuzz_depth = MAX_FUZZ_DEPTH                # type: int

    @property
    def seed(self) -> int:
        return self._seed

    @seed.setter
    def seed(self, value: int) -> None:
        self._seed = value
        core.global_force_seed = value      # type: ignore
        random.seed(value)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
