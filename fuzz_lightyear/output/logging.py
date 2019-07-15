import logging
from io import StringIO


def get_logger(name=None, format='%(message)s', propagate=True):
    """
    :type name: str
    :param name: used for declaring log channels.
    """
    log = logging.getLogger(name)
    log.propagate = propagate
    log.log_format = format

    # Bind custom method to instance.
    # Source: https://stackoverflow.com/a/2982
    log.set_debug_level = _set_debug_level.__get__(log)
    log.clear_stream = _clear_stream.__get__(log)

    log.handlers = []
    log.clear_stream()
    log.set_debug_level(0)

    return log


def _set_debug_level(self, debug_level):
    """
    :type debug_level: int, between 0-2
    :param debug_level: configure verbosity of log
    """
    mapping = {
        # Anything over INFO level.
        0: logging.INFO + 1,
        1: logging.INFO,
        2: logging.DEBUG,
    }

    self.setLevel(
        mapping[min(debug_level, 2)],
    )


def _clear_stream(self):
    """It's easier to create a new stream, rather than clearing it."""
    # Attach stream to log instance, so can be accessible publically.
    self.stream = StringIO()

    handler = logging.StreamHandler(self.stream)
    handler.setFormatter(
        logging.Formatter(self.log_format),
    )

    if not self.handlers:
        self.addHandler(handler)
    else:
        self.handlers[0] = handler


logging.captureWarnings(True)

# We distinguish the difference between the root logger, and this application
# specific logger. The root logger is for obtaining logged information from
# dependencies. In contrast, the application specific logger is for logging
# information during the normal process of this application.
root_logger = get_logger()
log = get_logger(
    'fuzz_lightyear',
    format='[%(module)s:%(lineno)d]\t%(levelname)s\t%(message)s',

    propagate=False,
)
