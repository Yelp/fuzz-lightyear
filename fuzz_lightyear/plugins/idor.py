from typing import Any
from typing import List

from bravado.exception import HTTPError
from bravado_core.exception import SwaggerMappingError      # type: ignore
from jsonschema.exceptions import ValidationError           # type: ignore

from ..datastore import get_non_vulnerable_operations
from ..request import FuzzingRequest
from ..response import ResponseSequence
from ..runner import run_sequence
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
        run_sequence(
            sequence=request_sequence[:-1],
            responses=ResponseSequence(),
            auth=get_abstraction().get_attacker_session(),  # type: ignore
        )
        try:
            request_sequence[-1].send(
                auth=get_abstraction().get_attacker_session(),  # type: ignore
                should_log=False,
            )
            return True

        except (HTTPError, SwaggerMappingError, ValidationError):
            return False
