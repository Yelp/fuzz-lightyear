"""
These endpoints focus on accepting a variety of different types of input.
"""
from flask_restplus import Resource

from ..core.extensions import api
from ..parsers.arrays import boolean_array_parser
from ..parsers.arrays import required_array_parser
from ..parsers.arrays import string_array_parser
from ..parsers.basic import primitive_query_parser
from ..util import get_name
from .models.basic import string_model


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

    @api.expect(required_array_parser)
    def put(self):
        return string_model.output()


@ns.route('/path_array/<array:ids>')
class ExpectPathArray(Resource):
    @api.doc(params={
        'ids': {
            'type': 'array',
            'collectionFormat': 'csv',
            'in': 'path',
            'items': {
                'type': 'integer',
            },
        },
    })
    def get(self, ids):
        return string_model.output()


# TODO: I would do an `object` endpoint (that's different than a post body),
#       but I don't know whether reqparse supports that.


@api.marshal_with(string_model.format)
@ns.route('/basic')
class ExpectPrimitives(Resource):
    @api.expect(primitive_query_parser)
    def get(self):
        return string_model.output()


@api.marshal_with(string_model.format)
@ns.route('/other')
class ExpectOtherPrimitives(Resource):
    @api.expect(primitive_query_parser)
    def get(self):
        return string_model.output()
