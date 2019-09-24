import sys

from .color import AnsiColor
from .color import colorize


def print_error(message: str) -> None:
    print(
        '{} {}'.format(
            colorize('error:', AnsiColor.RED),
            message,
        ),
        file=sys.stderr,
    )


def print_warning(message: str) -> None:
    print(
        '{} {}'.format(
            colorize('warning:', AnsiColor.YELLOW),
            message,
        ),
        file=sys.stderr,
    )
