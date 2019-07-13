from typing import Any
from typing import Dict
from typing import List

from .plugins import get_enabled_plugins
from .request import FuzzingRequest


class ResponseSequence:

    def __init__(self):
        self.responses = []     # type: List[Any]
        self.test_results = {}  # type: Dict[str, bool]

    def analyze_requests(
        self,
        request_sequence: List[FuzzingRequest],
    ) -> None:
        plugins = get_enabled_plugins()
        for plugin in plugins:
            if plugin.should_run(
                request_sequence,
                self.responses,
            ):
                self.test_results[plugin.__name__] = plugin.is_vulnerable(
                    request_sequence,
                    self.responses,
                )
