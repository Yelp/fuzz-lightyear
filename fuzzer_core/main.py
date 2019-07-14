from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests
import simplejson
from bravado.exception import HTTPError
from bravado_core.exception import SwaggerMappingError
from jsonschema.exceptions import ValidationError
from swagger_spec_validator.common import SwaggerValidationError

from .client import get_client
from .discovery import import_fixtures
from .generator import generate_sequences
from .output.interface import ResultFormatter
from .output.logging import log
from .output.util import print_error
from .runner import run_sequence
from .usage import parse_args


def main(argv: Optional[List[Any]] = None):
    args = parse_args(argv)
    if args.verbose:    # pragma: no cover
        log.set_debug_level(args.verbose)

    # Setup
    message = setup_client(args.url, args.schema)
    if message:
        print_error(message)
        return 1

    for fixture_path in args.fixture:
        import_fixtures(fixture_path)

    # Run
    outputter = ResultFormatter()
    for result in generate_sequences(
        n=args.iterations,
    ):
        try:
            result.responses = run_sequence(result.requests)
        except (HTTPError, SwaggerMappingError, ValidationError) as e:
            outputter.record_exception(result, e)

        outputter.record_result(result)

    outputter.show_results()

    return outputter.stats['failure'] != 0


def setup_client(
    url: str,
    schema: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    :returns: error message, if appropriate.
    """
    try:
        get_client(url=url, schema=schema)
    except requests.exceptions.ConnectionError:
        return 'Unable to connect to server.'
    except (simplejson.errors.JSONDecodeError, HTTPError):
        return (
            'Invalid swagger.json file. Please check to make sure the '
            'swagger file can be found at: {}.'.format(url)
        )
    except SwaggerValidationError:
        return 'Invalid swagger format.'
