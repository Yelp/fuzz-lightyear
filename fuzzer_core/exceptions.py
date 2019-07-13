class ConflictingKeys(ValueError):
    def __init__(self, key, *args, **kwargs):
        return super().__init__(
            'There are multiple factory registrations for "{}".'.format(key),
            *args,
            **kwargs,
        )
