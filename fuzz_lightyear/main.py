from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests
import simplejson
from bravado.client import SwaggerClient
from bravado.exception import HTTPError
from swagger_spec_validator.common import SwaggerValidationError    # type: ignore

from .discovery import import_fixtures
from .generator import generate_sequences
from .output.interface import ResultFormatter
from .output.logging import log
from .output.util import print_error
from .runner import run_sequence
from .settings import get_settings
from .supplements.abstraction import get_abstraction
from .usage import parse_args


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.verbose:    # pragma: no cover
        log.set_debug_level(args.verbose)

    # Setup
    message = setup_client(args.url, args.schema)
    if message:
        print_error(message)
        return 1

    setup_fixtures(args.fixture)
    outputter = run_tests(
        *args.test,
        iterations=args.iterations,
        seed=args.seed,
        ignore_exceptions=args.ignore_exceptions,
    )

    outputter.show_results()
    return outputter.stats['failure'] != 0


def setup_client(
    url: str,
    schema: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    :returns: error message, if appropriate.
    """
    if get_abstraction().client:
        return None

    try:
        config = {'internally_dereference_refs': True}
        if not schema:
            client = SwaggerClient.from_url(url, config=config)
        else:
            client = SwaggerClient.from_spec(schema, origin_url=url, config=config)
    except requests.exceptions.ConnectionError:
        return 'Unable to connect to server.'
    except (
        simplejson.errors.JSONDecodeError,      # type: ignore
        HTTPError,
    ):
        return (
            'Invalid swagger.json file. Please check to make sure the '
            'swagger file can be found at: {}.'.format(url)
        )
    except SwaggerValidationError:
        return 'Invalid swagger format.'

    get_abstraction().client = client
    return None


def setup_fixtures(fixtures: List[str]) -> None:
    for fixture_path in fixtures:
        import_fixtures(fixture_path)


def run_tests(
    *tests: str,
    iterations: int = 1,
    seed: int = None,
    ignore_exceptions: bool = False,
) -> ResultFormatter:
    """
    :param tests: list of tests to run.
        e.g. `basic.get_private_listing`

    :param iterations: size of request sequence to generate.
    :param seed: used for random generation of test input
    :param ignore_exceptions: if True, ignores HTTP exceptions to requests.
    """
    if seed is not None:
        get_settings().seed = seed

    outputter = ResultFormatter()
    for result in generate_sequences(
        n=iterations,
        tests=tests,
    ):
        try:
            run_sequence(result.requests, result.responses)
        except Exception as e:
            if (
                ignore_exceptions and
                isinstance(e, HTTPError)
            ):
                # This makes it look like a valid request sequence.
                result.responses.responses = result.requests
            else:
                outputter.record_exception(result, e)

        outputter.record_result(result)

    return outputter
