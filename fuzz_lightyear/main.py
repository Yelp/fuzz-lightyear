import warnings
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests
import simplejson
import yaml
from bravado.client import SwaggerClient
from bravado.exception import HTTPError
from hypothesis.errors import NonInteractiveExampleWarning
from swagger_spec_validator.common import SwaggerValidationError    # type: ignore

from .datastore import get_excluded_operations
from .datastore import get_non_vulnerable_operations
from .datastore import get_setup_fixtures
from .discovery import import_fixtures
from .generator import generate_sequences
from .output.interface import ResultFormatter
from .output.logging import log
from .output.util import print_error
from .runner import validate_sequence
from .settings import get_settings
from .supplements.abstraction import get_abstraction
from .usage import parse_args


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.verbose:    # pragma: no cover
        log.set_debug_level(args.verbose)

    # NOTE: Hypothesis warns us against using `.example()` (which we leverage
    # during the fuzzing process), and to use `@given` instead. However, we
    # are not using hypothesis in a conventional manner, and therefore this
    # warning does not apply to us.
    warnings.filterwarnings('ignore', category=NonInteractiveExampleWarning)

    # Setup
    message = setup_client(args.url, args.schema)
    if message:
        print_error(message)
        return 1

    setup_fixtures(args.fixture)
    run_user_defined_setup()
    if args.ignore_non_vulnerable:
        get_excluded_operations().update(
            get_non_vulnerable_operations(),
        )

    outputter = run_tests(
        *args.test,
        iterations=args.iterations,
        seed=args.seed,
        ignore_exceptions=args.ignore_exceptions,
        disable_unicode=args.disable_unicode,
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
        yaml.YAMLError,
        HTTPError,
    ):
        return (
            'Invalid swagger file. Please check to make sure the '
            'swagger file can be found at: {}.'.format(url)
        )
    except SwaggerValidationError:
        return 'Invalid swagger format.'

    get_abstraction().client = client
    return None


def setup_fixtures(fixtures: List[str]) -> None:
    for fixture_path in fixtures:
        import_fixtures(fixture_path)


def run_user_defined_setup() -> None:
    for function in get_setup_fixtures():
        function()


def run_tests(
    *tests: str,
    iterations: int = 1,
    seed: int = None,
    ignore_exceptions: bool = False,
    disable_unicode: bool = False,
) -> ResultFormatter:
    """
    :param tests: list of tests to run.
        e.g. `basic.get_private_listing`

    :param iterations: size of request sequence to generate.
    :param seed: used for random generation of test input
    :param ignore_exceptions: if True, ignores HTTP exceptions to requests.
    :param disable_unicode: if True, only use ASCII characters to fuzz strings
    """
    if seed is not None:
        get_settings().seed = seed
    if disable_unicode:
        get_settings().unicode_enabled = False

    outputter = ResultFormatter()
    for result in generate_sequences(
        n=iterations,
        tests=tests,
    ):
        try:
            validate_sequence(result.requests, result.responses)
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
