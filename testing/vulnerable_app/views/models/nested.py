from flask_restplus import fields

from ...core.extensions import api
from .basic import session_model


UserModel = api.model(
    'UserModel',
    {
        'name': fields.String,
        'info': fields.Nested(session_model.format),
    },
)
