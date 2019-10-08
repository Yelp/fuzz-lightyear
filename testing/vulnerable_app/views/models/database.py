from flask_restplus import fields

from ...core.extensions import api


user_model = api.model(
    'User',

    # Additional keys are supported. The library just needs something to
    # label the object returned, otherwise, the response will just be `None`.
    # NOTE: In addition, this dictionary cannot be empty.
    {
        'user_id': fields.Integer(required=True),
    },
)

widget_model = api.model(
    'Widget',
    {
        'id': fields.Integer(required=True),
    },
)
