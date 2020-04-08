from enum import Enum

from fuzz_lightyear.settings import get_settings


class AnsiColor(Enum):
    RESET = '[0m'
    BOLD = '[1m'
    RED = '[91m'
    RED_BACKGROUND = '[41m'
    YELLOW = '[33m'
    LIGHT_GREEN = '[92m'
    PURPLE = '[95m'


def colorize(text: str, color: AnsiColor) -> str:
    if not get_settings().enable_color:
        return text

    return '\x1b{}{}\x1b{}'.format(
        color.value,
        text,
        AnsiColor.RESET.value,
    )
