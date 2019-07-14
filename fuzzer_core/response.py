from typing import Any
from typing import Dict
from typing import List

from .plugins import get_enabled_plugins
from .request import FuzzingRequest


class ResponseSequence:

    def __init__(self):
        # Collection of response objects returned by API calls.
        self.responses = []     # type: List[Any]

        # Collection of items produced through making requests
        self.data = {}          # type: Dict[str, Any]

        # Result of analysis done on responses received
        self.test_results = {}  # type: Dict[str, bool]

    def add_response(self, response):
        self.responses.append(response)
        for key in dir(response):
            self.data[key] = getattr(response, key)

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
