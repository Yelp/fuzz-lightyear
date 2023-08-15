from typing import Any
from typing import Dict  # noqa: F401
from typing import List

from .request import FuzzingRequest


class ResponseSequence:

    def __init__(self) -> None:
        # Collection of response objects returned by API calls.
        self.responses = []     # type: List[Any]

        # Collection of items produced through making requests
        self.data = {}          # type: Dict[str, Any]

        # Result of analysis done on responses received
        self.test_results = {}  # type: Dict[str, bool]

    def __len__(self) -> int:
        return len(self.responses)

    def add_response(self, response: Any) -> None:
        self.responses.append(response)
        if not response:
            return

        for key in dir(response):
            self.data[key] = getattr(response, key)

    def analyze_requests(
        self,
        request_sequence: List[FuzzingRequest],
    ) -> None:
        # We import here because otherwise we run into a circular dependency
        from .plugins import get_enabled_plugins
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
