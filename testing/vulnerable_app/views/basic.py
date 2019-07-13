"""
Basic, straight forward endpoints for MVP testing.
"""
from flask import request
from flask_restplus import fields
from flask_restplus import Resource

from ..core.extensions import api
from ..util import get_name


ns = api.namespace(
    get_name(__name__),
    url_prefix='/{}'.format(get_name(__name__)),
)


@ns.route('/')
class NoInputsRequired(Resource):
    @api.marshal_with(
        api.model(
            'GetNoInputsRequired',
            {
                'value': fields.String,
            },
        ),
    )
    def get(self):
        return {
            'value': request.cookies.get('zss', ''),
        }
