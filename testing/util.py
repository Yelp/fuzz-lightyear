import re


# Source: https://stackoverflow.com/a/14693789
_ansi_escape = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')


def uncolor(text):
    return _ansi_escape.sub('', text)
