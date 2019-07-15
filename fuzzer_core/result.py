from typing import Dict
from typing import List
from typing import Optional

from .request import FuzzingRequest
from .response import ResponseSequence


class FuzzingResult:
    def __init__(
        self,
        request_sequence: List[FuzzingRequest],
    ):
        self.requests = request_sequence    # type: List[FuzzingRequest]
        self.responses = None               # type: Optional[ResponseSequence]

        self.log_output = ''
        self.exception_info = {}            # type: Dict[str, str]

    def is_successful(self) -> bool:
        return bool(self.responses)
