from flask import request
from flask_restplus import fields

from . import Model
from ...core.extensions import api


string_model = Model(
    format=api.model(
        'BasicStringOutput',
        {
            'value': fields.String(required=True),
        },
    ),
    output=lambda: {
        'value': 'ok',
    },
)


session_model = Model(
    format=api.model(
        'SessionCookieOutput',
        {
            'session': fields.String,
        },
    ),
    output=lambda: {
        'session': request.cookies.get('session', ''),
    },
)


variable_string_model = Model(
    format=api.model(
        'VariableResultOutput',
        {
            'value': fields.String,
        },
    ),
    output=lambda x: {
        'value': str(x),
    },
)
