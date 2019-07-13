"""
These endpoints return the same value, no matter the input.
"""
from flask_restplus import Resource

from ..core.extensions import api
from ..models.basic import string_model
from ..util import get_name


ns = api.namespace(
    get_name(__name__),
    url_prefix='/{}'.format(get_name(__name__)),
)


@ns.route('/')
class NoInputsRequired(Resource):
    @api.marshal_with(string_model.format)
    def get(self):
        return string_model.output()
