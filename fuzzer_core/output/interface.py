import sys
import traceback
from collections import Counter
from datetime import datetime

from . import formatter
from ..result import FuzzingResult
from .color import AnsiColor
from .color import colorize
from .logging import log
from .logging import root_logger


class ResultFormatter:
    def __init__(self):
        print(
            colorize(
                formatter.format_header('fuzzing session starts', header_line='='),
                AnsiColor.BOLD,
            ),
        )

        self.current_tag = None

        self.stats = Counter()
        self.start_time = datetime.now()

        self.warnings = []
        self.vulnerable_results = []

    def record_result(self, result: FuzzingResult):
        # Change tag, if appropriate.
        current_tag = result.requests[0].tag
        if current_tag != self.current_tag:
            prefix = '\n' if self.current_tag else ''
            print(f'{prefix}{current_tag} ', end='')

            self.current_tag = current_tag

        # Show status as tests pass/fail.
        is_successful = False
        if (
            result.responses and
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
            log.clear_stream()

            self.vulnerable_results.append(result)

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
    ):
        result.exception_info = {
            'name': e.__class__.__name__,
            'traceback': ''.join(
                traceback.format_exception(
                    *sys.exc_info(),
                ),
            ).strip(),
        }

    def show_results(self):
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
