from typing import List

from .request import FuzzingRequest
from .response import ResponseSequence


class FuzzingResult:
    def __init__(
        self,
        request_sequence: List[FuzzingRequest],
    ):
        self.requests = request_sequence    # type: List[FuzzingRequest]
        self.responses = None               # type: List[ResponseSequence]

    def is_successful(self) -> bool:
        return bool(self.responses)
