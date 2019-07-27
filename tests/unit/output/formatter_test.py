import textwrap
from contextlib import contextmanager
from datetime import timedelta
from unittest import mock

import pytest

from fuzz_lightyear.output import formatter
from fuzz_lightyear.request import FuzzingRequest
from fuzz_lightyear.response import ResponseSequence
from fuzz_lightyear.result import FuzzingResult
from fuzz_lightyear.supplements.abstraction import get_abstraction
from testing.util import uncolor


class TestFormatResults:
    def test_no_results(self):
        with nicer_output():
            assert formatter.format_results([]) == ''

    def test_basic(self, mock_client):
        with nicer_output():
            assert uncolor(
                formatter.format_results([
                    self.mock_result(
                        {
                            'operation_id': 'get_one',
                            'id': 1,
                        },
                        test_results={
                            'IDORPlugin': True,
                        },
                        client=mock_client,
                    ),
                ]),
            ) == textwrap.dedent("""
                Test Failures
                test.get_one [IDORPlugin]
                Request Sequence:
                [
                  "curl -X GET http://localhost:80/test/get_one?id=1"
                ]
            """)[1:]

    def test_multiple_failures(self, mock_client):
        with nicer_output():
            assert uncolor(
                formatter.format_results([
                    self.mock_result(
                        {
                            'operation_id': 'post_one',
                            'id': 1,
                        },
                        test_results={
                            'IDORPlugin': True,
                        },
                        client=mock_client,
                    ),
                    self.mock_result(
                        {
                            'operation_id': 'get_two',
                        },
                        {
                            'operation_id': 'post_one',
                            'id': 2,
                        },
                        test_results={
                            'IDORPlugin': True,
                        },
                        client=mock_client,
                    ),
                ]),
            ) == textwrap.dedent("""
                Test Failures
                test.post_one [IDORPlugin]
                Request Sequence:
                [
                  "curl -X POST http://localhost:80/test/post_one --data 'id=1'"
                ]
                test.post_one [IDORPlugin]
                Request Sequence:
                [
                  "curl -X GET http://localhost:80/test/get_two",
                  "curl -X POST http://localhost:80/test/post_one --data 'id=2'"
                ]
            """)[1:]

    def test_exception_display(self):
        result = self.mock_result(
            {
                'operation_id': 'one',
            },
        )
        result.exception_info = {
            'name': 'TestException',
            'traceback': 'hi',
        }

        with nicer_output():
            assert uncolor(formatter.format_results([result])) == textwrap.dedent("""
                Test Failures
                test.one [TestException]
                hi
            """)[1:]

    def test_logging_output(self, mock_client):
        result = self.mock_result(
            {
                'operation_id': 'get_one',
            },
            test_results={
                'IDORPlugin': True,
            },
            client=mock_client,
        )
        result.log_output = 'hello'

        with nicer_output():
            assert uncolor(formatter.format_results([result])) == textwrap.dedent("""
                Test Failures
                test.get_one [IDORPlugin]
                Request Sequence:
                [
                  "curl -X GET http://localhost:80/test/get_one"
                ]
                Captured log calls
                hello
            """)[1:]

    def mock_result(self, *cases, test_results=None, client=None):
        request_sequence = []
        for case in cases:
            request_sequence.append(
                FuzzingRequest(
                    tag='test',
                    **case,
                ),
            )

            if client:
                setattr(
                    client.test,
                    case['operation_id'],
                    self.mock_client_properties(**case),
                )

        result = FuzzingResult(request_sequence)
        result.responses = ResponseSequence()
        if test_results:
            result.responses.test_results = test_results

        return result

    @pytest.fixture(autouse=True)
    def mock_client(self):
        client = mock.Mock()
        get_abstraction().client = client
        yield client

    def mock_client_properties(self, operation_id, **kwargs):
        output = mock.Mock()
        output.swagger_spec.api_url = 'http://localhost:80/'
        output.path_name = f'/test/{operation_id}'

        output.http_method = 'get'
        if operation_id.startswith('post_'):
            output.http_method = 'post'

        output.params = {}
        for key in kwargs:
            param = mock.Mock()
            param.location = 'query'
            if output.http_method == 'post':
                param.location = 'formData'

            output.params[key] = param

        return output


def test_format_warnings():
    with nicer_output():
        assert uncolor(
            formatter.format_warnings([
                'beef\n',
                'cake',
            ]),
        ) == textwrap.dedent("""
            warnings summary
            beef
            cake
        """)[1:-1]


@pytest.mark.parametrize(
    'args, expected',
    (
        # All tests pass
        (
            (
                {
                    'success': 5,
                    'failure': 0,
                    'warnings': 0,
                },
                timedelta(seconds=1),
            ),
            '5 passed in 1.0 seconds',
        ),

        # All tests fail
        (
            (
                {
                    'success': 0,
                    'failure': 5,
                    'warnings': 0,
                },
                timedelta(seconds=1, microseconds=52 * 1000 * 10),
            ),
            '5 failed in 1.52 seconds',
        ),

        # Failures found
        (
            (
                {
                    'success': 3,
                    'failure': 2,
                    'warnings': 0,
                },
                timedelta(seconds=1),
            ),
            '2 failed, 3 passed in 1.0 seconds',
        ),

        # Warnings found.
        # There are many other iterations, but mostly needs to test
        # for colors.
        (
            (
                {
                    'success': 3,
                    'failure': 2,
                    'warnings': 1,
                },
                timedelta(seconds=1),
            ),
            '2 failed, 3 passed, 1 warnings in 1.0 seconds',
        ),
    ),
)
def test_format_summary(args, expected):
    with nicer_output():
        assert uncolor(
            formatter.format_summary(*args),
        ) == expected


class TestFormatHeader:

    def test_even(self):
        with self.mock_terminal_width(10):
            assert formatter.format_header('hello') == '= hello ='
            assert formatter.format_header('beef') == '== beef =='

    def test_odd(self):
        with self.mock_terminal_width(9):
            assert formatter.format_header('hello') == '= hello ='
            assert formatter.format_header('beef') == '= beef ='

    def test_no_space_for_padding(self):
        with self.mock_terminal_width(5):
            assert formatter.format_header('hello') == ' hello '

    @staticmethod
    @contextmanager
    def mock_terminal_width(value):
        with mock.patch.object(
            formatter,
            '_get_terminal_width',
            return_value=value,
        ):
            yield


class TestFormatWarning:

    def test_no_warnings(self):
        assert formatter.format_warning(
            'does_not.matter',
            '',
        ) == ''

    def test_basic(self):
        """
        Unfornuately, we can't do anything more complicated than this
        (e.g. with the `warnings` module), because I think pytest does
        some hackery and captures all the warnings (so it won't appear
        here).
        """
        assert formatter.format_warning(
            'hello.world',
            '/tests/core/output/formatter_test.py:1 Warning: DUCK!\n',
        ) == textwrap.dedent("""
            hello.world
              /tests/core/output/formatter_test.py:1 Warning: DUCK!
        """)[1:]


@contextmanager
def nicer_output():
    original_function = formatter.format_header

    def strip_padding(message, *args, **kwargs):
        """
        This function is needed, because pre-commit strips trailing spaces.
        """
        output = original_function(message, *args, **kwargs)
        return output[1:-1]

    with mock.patch.object(
        # Make sure that no extra padding is used.
        formatter,
        '_get_terminal_width',
        return_value=0,
    ), mock.patch.object(
        # This removes spaces from the header.
        formatter,
        'format_header',
        strip_padding,
    ):
        yield
