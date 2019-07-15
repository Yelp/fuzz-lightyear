from abc import ABCMeta
from abc import abstractstaticmethod
from typing import Any
from typing import List

from ..request import FuzzingRequest


class BasePlugin(metaclass=ABCMeta):

    @staticmethod
    def should_run(request_sequence, response_sequence):
        return True

    @abstractstaticmethod
    def is_vulnerable(
        self,
        request_sequence: List[FuzzingRequest],
        response_sequence: List[Any],
    ) -> bool:
        pass
