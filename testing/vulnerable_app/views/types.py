"""
These endpoints focus on accepting a variety of different types of input.
"""
from flask_restplus import Resource

from ..core.extensions import api
from ..models.basic import string_model
from ..parsers.arrays import boolean_array_parser
from ..parsers.arrays import string_array_parser
from ..parsers.basic import primitive_query_parser
from ..util import get_name


ns = api.namespace(
    get_name(__name__),
    url_prefix='/{}'.format(get_name(__name__)),
)


@api.marshal_with(string_model.format)
@ns.route('/array')
class ExpectArray(Resource):
    @api.expect(boolean_array_parser)
    def get(self):
        return string_model.output()

    @api.expect(string_array_parser)
    def post(self):
        return string_model.output()


# TODO: I would do an `object` endpoint, but I don't know whether reqparse
#       supports that.


@api.marshal_with(string_model.format)
@ns.route('/basic')
class ExpectPrimitives(Resource):
    @api.expect(primitive_query_parser)
    def get(self):
        return string_model.output()
