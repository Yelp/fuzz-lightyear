from abc import ABCMeta
from typing import Any
from typing import List

from ..request import FuzzingRequest


class BasePlugin(metaclass=ABCMeta):

    @staticmethod
    def should_run(
        request_sequence: List[FuzzingRequest],
        response_sequence: List[Any],
    ) -> bool:
        return True

    @staticmethod
    def is_vulnerable(
        request_sequence: List[FuzzingRequest],
        response_sequence: List[Any],
    ) -> bool:
        raise NotImplementedError
