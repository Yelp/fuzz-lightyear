import logging
from io import StringIO
from typing import Any


class CustomLogger:
    """
    This shims `logging.Logger` without using inheritance, since we want to
    leverage `logging.getLogger`.
    """

    def __init__(
        self,
        log: logging.Logger,
        log_format: str = '%(message)s',
    ) -> None:
        # To prevent infinite recursion, we explicitly call `object`'s setattr.
        # This also sets it as an instance variable, rather than calling the
        # CustomLogger's `__setattr__`, which will set it as a variable on
        # `self.log`.
        super().__setattr__('log', log)
        super().__setattr__('log_format', log_format)

    def set_debug_level(self, debug_level: int) -> None:
        """
        :param debug_level: configure verbosity of log (between 0-2)
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

    def clear_stream(self) -> None:
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

    def __getattr__(self, name: str) -> Any:
        return getattr(self.log, name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self.log, name, value)


def get_logger(
    name: str = None,
    format: str = '%(message)s',
    propagate: bool = True,
) -> CustomLogger:
    """
    :param name: used for declaring log channels.
    """
    log = CustomLogger(
        logging.getLogger(name),
        log_format=format,
    )
    log.propagate = propagate

    log.handlers = []
    log.clear_stream()
    log.set_debug_level(0)

    return log


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
