from collections import namedtuple


Model = namedtuple(
    'Model',
    (
        # This is passed into @api.marshal_with, and specifies Swagger spec.
        'format',

        # This is the output for the endpoint.
        'output',
    ),
)
