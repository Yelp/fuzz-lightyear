import json
import logging
import subprocess
import sys
import textwrap
from datetime import timedelta
from functools import lru_cache
from typing import List
from typing import MutableMapping
from typing import Tuple

from ..result import FuzzingResult
from .color import AnsiColor
from .color import colorize
from .logging import log


def format_results(
    results: List[FuzzingResult],
) -> str:
    """Used to output final results."""
    if not results:
        return ''

    sequences_output = ''
    for result in results:
        name, info = _format_result(result)
        sequences_output += textwrap.dedent("""
            {header}
            {info}
        """)[1:].format(
            header=colorize(
                format_header(
                    '{} [{}]'.format(
                        result.requests[-1].id,
                        name,
                    ),
                    header_line='_',
                ),
                AnsiColor.RED,
            ),
            info=info,
        )

        if not result.log_output:
            continue

        sequences_output += textwrap.dedent("""
            {header}
            {logs}
        """)[1:].format(
            header=format_header(
                'Captured log calls',
                header_line='-',
            ),
            logs=result.log_output,
        )

    return textwrap.dedent("""
        {section_header}
        {sequences}
    """)[1:-1].format(
        section_header=format_header('Test Failures'),
        sequences=sequences_output,
    )


def _format_result(result: FuzzingResult) -> Tuple[str, str]:
    if result.exception_info:
        info = [
            result.exception_info['traceback'],
        ]

        if log.level <= logging.INFO:
            info = [
                'Input:',
                json.dumps(result.exception_info['parameters'], indent=2),
                '',
                *info,
            ]

        return (
            result.exception_info['name'],
            '\n'.join(info),
        )

    return (
        ','.join([
            key
            for key, value in result.responses.test_results.items()
            if value
        ]),
        textwrap.dedent("""
            {request_sequence_header}
            {request_json_dump}
        """)[1:-1].format(
            request_sequence_header=colorize(
                'Request Sequence:',
                AnsiColor.BOLD,
            ),
            request_json_dump=json.dumps(
                [
                    str(request)
                    for request in result.requests
                ],
                indent=2,
            ),
        ),
    )


def format_warnings(warnings: List[str]) -> str:
    """Used to output aggregated warnings."""
    return textwrap.dedent("""
        {header}
        {content}
    """)[1:-1].format(
        header=colorize(
            format_header('warnings summary'),
            AnsiColor.YELLOW,
        ),
        content=''.join(warnings),
    )


def format_summary(
    stats: MutableMapping[str, int],
    timing: timedelta,
) -> str:
    num_passed = stats['success']
    num_failures = stats['failure']
    num_warnings = stats['warnings']

    color = AnsiColor.RESET
    summary = []
    if num_passed:
        summary.append(f'{num_passed} passed')
        color = AnsiColor.LIGHT_GREEN

    if num_warnings:
        summary.append(f'{num_warnings} warnings')
        color = AnsiColor.YELLOW

    if num_failures:
        summary = [f'{num_failures} failed', *summary]
        color = AnsiColor.RED

    if not summary:
        return colorize(format_header('No tests run!'), AnsiColor.BOLD)

    if color == AnsiColor.RESET:
        summary_string = 'No tests run'
    else:
        summary_string = '{} in {} seconds'.format(
            ', '.join(summary),
            round(timing.total_seconds(), 2),
        )

    return colorize(
        colorize(
            format_header(summary_string),
            color,
        ),
        AnsiColor.BOLD,
    )


def format_header(
    message: str,
    header_line: str = '=',
) -> str:
    """
    Creates messages like:
        ========== header text here ==========
    """
    width = _get_terminal_width()

    # Pad the message with single space on both ends, for nicer output.
    message = f' {message} '

    if len(message) >= width:
        return message

    # Add header_line to fill up space.
    padding_length = width - len(message)
    if padding_length % 2 == 1:
        padding_length -= 1

    padding_per_side = padding_length // 2
    return '{}{}{}'.format(
        padding_per_side * header_line,
        message,
        padding_per_side * header_line,
    )


@lru_cache(maxsize=1)
def _get_terminal_width() -> int:  # pragma: no cover
    """
    Source: https://gist.github.com/Steelsouls/9626112
    """
    try:
        width = subprocess.check_output('tput cols'.split())
    except OSError as e:
        print(
            f'Invalid Command: tput: exit status ({e.errno})',
            file=sys.stderr,
        )
    except subprocess.CalledProcessError as e:
        print(
            f'Invalid Command: tput: exit status ({e.returncode})',
            file=sys.stderr,
        )
    else:
        return int(width.decode('utf-8'))

    return 0


def format_warning(
    test_id: str,
    warning: str,
) -> str:
    """
    Formats warning messages for a single endpoint.
    Example Output:
        basic.get_private_listing
          /path/to/file.py:345 Warning: This is a warning message!
    """
    if not warning:
        return ''

    return textwrap.dedent(f"""
        {test_id}
          {warning}
    """)[1:-1]
