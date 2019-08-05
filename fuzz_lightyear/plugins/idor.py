from typing import Any
from typing import List

from bravado.exception import HTTPError
from bravado_core.exception import SwaggerMappingError      # type: ignore
from jsonschema.exceptions import ValidationError           # type: ignore

from ..request import FuzzingRequest
from ..supplements.abstraction import get_abstraction
from .base import BasePlugin


class IDORPlugin(BasePlugin):

    @staticmethod
    def should_run(
        request_sequence: List[FuzzingRequest],
        response_sequence: List[Any],
    ) -> bool:
        last_request = request_sequence[-1]

        # If there are no parameters, then there's no way to
        # specify what victim resources to try to steal / modify.
        return bool(last_request.fuzzed_input)

    @staticmethod
    def is_vulnerable(
        request_sequence: List[FuzzingRequest],
        response_sequence: List[Any],
    ) -> bool:
        last_request = request_sequence[-1]
        try:
            last_request.send(
                auth=get_abstraction().get_attacker_session(),
                should_log=False,
            )

            return True
        except (HTTPError, SwaggerMappingError, ValidationError):
            return False
