"""
These endpoints return the same value, no matter the input.
"""
from flask import abort
from flask_restplus import Resource

from ..core.extensions import api
from ..parsers.error import error_code_parser
from ..util import get_name
from .models.basic import string_model


ns = api.namespace(
    get_name(__name__),
    url_prefix='/{}'.format(get_name(__name__)),
)


@ns.route('/')
class NoInputsRequired(Resource):
    @api.marshal_with(string_model.format)
    def get(self):
        return string_model.output()


@ns.route('/error')
@api.response(400, 'Bad Request.')
@api.response(401, 'Unauthorized.')
@api.response(403, 'Forbidden.')
@api.response(404, 'Not Found.')
@api.response(500, 'Internal Server Error.')
class WillThrowError(Resource):
    @api.expect(error_code_parser)
    def get(self):
        args = error_code_parser.parse_args()
        abort(args.code)
