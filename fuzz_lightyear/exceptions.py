class BaseFuzzingError(Exception):
    """This exists so that clients can distinguish between exception classes."""


class ConflictingKeys(BaseFuzzingError):
    def __init__(self, key, *args, **kwargs):
        return super().__init__(
            'There are multiple factory registrations for "{}".'.format(key),
            *args,
            **kwargs,
        )


class ConflictingHandlers(BaseFuzzingError):
    def __init__(self, key, *args, **kwargs):
        return super().__init__(
            'There are multiple handlers registered for "{}".'.format(key),
            *args,
            **kwargs,
        )
