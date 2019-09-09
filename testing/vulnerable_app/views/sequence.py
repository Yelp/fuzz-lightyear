"""
These endpoints focus on testing the stateful-ness of the fuzzer.

The `alpha` series of endpoints enforce basic stateful-ness.
"""
from flask_restplus import reqparse
from flask_restplus import Resource

from ..core.extensions import api
from ..models.basic import string_model
from ..util import get_name


ns = api.namespace(
    get_name(__name__),
    url_prefix='/{}'.format(get_name(__name__)),
)


@api.marshal_with(string_model.format)
@ns.route('/alpha/one')
class AlphaOne(Resource):
    def post(self):
        return string_model.output()


alpha_two_parser = reqparse.RequestParser()
alpha_two_parser.add_argument(
    'value',
    location='args',
)


@ns.route('/alpha/two')
class AlphaTwo(Resource):
    @api.expect(alpha_two_parser)
    @api.response(200, 'Success', model=str)
    def get(self):
        return alpha_two_parser.parse_args()['value']
