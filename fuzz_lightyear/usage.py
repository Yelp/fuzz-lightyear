import argparse
import json
import os

from fuzz_lightyear import VERSION


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        '--verbose',
        help='Increase the verbosity of logging.',
        action='count',
    )
    parser.add_argument(
        '--version',
        action='version',
        version=VERSION,
        help='Displays version information.',
    )

    parser.add_argument(
        'url',
        type=str,
        help='URL of server to fuzz.',
    )
    parser.add_argument(
        '-n',
        '--iterations',
        nargs='?',
        default=1,
        help='Maximum request sequence length to fuzz.',
        type=int,
    )
    parser.add_argument(
        '--schema',
        help=(
            'Path to local swagger schema. If provided, this overrides the'
            'swagger file found at the URL.'
        ),
        type=_is_valid_schema,
    )

    parser.add_argument(
        '-f',
        '--fixture',
        action='append',
        default=[],
        help='Path to custom specified fixtures.',
        type=_is_valid_path,
    )

    parser.add_argument(
        '--seed',
        type=int,
        help='Specify seed for generation of random output.',
    )
    parser.add_argument(
        '-t',
        '--test',
        type=str,
        default=[],
        action='append',
        help='Specifies a single test to run.',
    )

    return parser.parse_args(argv)


def _is_valid_schema(path):
    _is_valid_path(path)
    with open(path) as f:
        try:
            return json.loads(f.read())
        except json.decoder.JSONDecodeError:
            raise argparse.ArgumentTypeError(
                'Invalid JSON file: {}'.format(path),
            )


def _is_valid_path(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(
            'Invalid path: {}'.format(path),
        )

    return path