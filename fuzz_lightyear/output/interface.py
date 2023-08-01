import sys
import textwrap
import traceback
from collections import Counter
from datetime import datetime
from typing import List  # noqa: F401
from typing import Optional  # noqa: F401

from . import formatter
from ..result import FuzzingResult
from ..settings import get_settings
from .color import AnsiColor
from .color import colorize
from .logging import log
from .logging import root_logger


class ResultFormatter:
    def __init__(self) -> None:
        if not sys.stdout.isatty():
            get_settings().enable_color = False

        print(
            colorize(
                formatter.format_header('fuzzing session starts', header_line='='),
                AnsiColor.BOLD,
            ),
        )
        print(_get_info())

        self.current_tag = None         # type: Optional[str]

        self.stats = Counter()          # type: Counter
        self.start_time = datetime.now()

        self.warnings = []              # type: List[str]
        self.vulnerable_results = []    # type: List[FuzzingResult]

    def record_result(self, result: FuzzingResult) -> None:
        # Change tag, if appropriate.
        current_tag = result.requests[0].tag
        if current_tag != self.current_tag:
            prefix = '\n' if self.current_tag else ''
            print(f'{prefix}{current_tag} ', end='')

            self.current_tag = current_tag

        # Show status as tests pass/fail.
        is_successful = False
        if (
            len(result.responses) == len(result.requests) and
            not any(result.responses.test_results.values())
        ):
            is_successful = True

        # Record stats for summary output.
        if is_successful:
            print(colorize('.', AnsiColor.LIGHT_GREEN), end='')
            self.stats['success'] += 1
        else:
            print(colorize('E', AnsiColor.RED), end='')
            self.stats['failure'] += 1

            result.log_output = log.stream.getvalue()

            self.vulnerable_results.append(result)

        # Clear log after every run.
        log.clear_stream()

        # Aggregate warnings for summary output.
        self.warnings.append(
            formatter.format_warning(
                f'{result.requests[-1].id}',
                root_logger.stream.getvalue(),
            ),
        )
        root_logger.clear_stream()

    def record_exception(
        self,
        result: FuzzingResult,
        e: BaseException,
    ) -> None:
        # If there's an exception, it means that the first request failed after
        # a sequence of successful requests.
        parameters = result.requests[len(result.responses.responses) - 1].fuzzed_input
        result.exception_info = {
            'name': e.__class__.__name__,
            'traceback': ''.join(
                traceback.format_exception(
                    *sys.exc_info(),
                ),
            ).strip(),
            'parameters': parameters,
        }

    def show_results(self) -> None:
        print()

        print(formatter.format_results(self.vulnerable_results))

        warnings = list(filter(bool, self.warnings))
        if warnings:
            print(formatter.format_warnings(warnings))

        self.stats['warnings'] = len(warnings)
        print(
            formatter.format_summary(
                self.stats,
                datetime.now() - self.start_time,
            ),
        )


def _get_info() -> str:
    return textwrap.dedent(f"""
        Hypothesis Seed: {get_settings().seed}
    """)[1:]
