"""
Basic, straight forward endpoints for MVP testing.
"""
from flask_restplus import Resource

from ..core.extensions import api
from ..parsers.basic import number_query_parser
from ..util import get_name
from .models.basic import session_model
from .models.basic import variable_string_model


ns = api.namespace(
    get_name(__name__),
    url_prefix='/{}'.format(get_name(__name__)),
)


@ns.route('/')
class NoInputsRequired(Resource):
    @api.marshal_with(session_model.format)
    def get(self):
        return session_model.output()


@ns.route('/post')
class PublicListing(Resource):
    @api.expect(number_query_parser)
    @api.marshal_with(variable_string_model.format)
    def get(self):
        args = number_query_parser.parse_args()
        return variable_string_model.output(args.id)


@ns.route('/account')
class PrivateListing(Resource):
    @api.expect(number_query_parser)
    @api.marshal_with(session_model.format)
    def get(self):
        return session_model.output()
