from typing import Any
from typing import List

from bravado.exception import HTTPError
from bravado_core.exception import SwaggerMappingError      # type: ignore
from jsonschema.exceptions import ValidationError           # type: ignore

from ..datastore import get_non_vulnerable_operations
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

        # If an operation is marked is non-vulnerable, we don't need
        # to check if it's vulnerable.
        if last_request.operation_id in get_non_vulnerable_operations():
            return False

        # If there are no parameters, then there's no way to
        # specify what victim resources to try to steal / modify.
        return bool(last_request.fuzzed_input)

    @staticmethod
    def is_vulnerable(
        request_sequence: List[FuzzingRequest],
        response_sequence: List[Any],
    ) -> bool:
        # We have the attacker execute the same request sequence with different
        # values except for the last request.
        for request in request_sequence[:-1]:
            if request.fuzzed_input:
                for query_key in request.fuzzed_input:
                    request.fuzzed_input[query_key] += 1
        for request in request_sequence:
            try:
                request.send(
                    auth=get_abstraction().get_attacker_session(),  # type: ignore
                    should_log=False,
                )

            except (HTTPError, SwaggerMappingError, ValidationError):
                return False
        return True
