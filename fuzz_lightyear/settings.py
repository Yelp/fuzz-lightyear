import random
from functools import lru_cache

from hypothesis import core


@lru_cache(maxsize=1)
def get_settings():
    return Settings()


class Settings:
    def __init__(self):
        self.seed = random.getrandbits(128)    # type: int

    @property
    def seed(self) -> int:
        return self._seed

    @seed.setter
    def seed(self, value: int):
        self._seed = value
        core.global_force_seed = value      # type: ignore
        random.seed(value)
