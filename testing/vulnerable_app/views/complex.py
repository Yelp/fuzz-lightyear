"""
These endpoints focus on nested and more complicated inputs.
"""
from flask_restplus import Resource

from ..core.extensions import api
from ..models.nested import UserModel
from ..util import get_name


ns = api.namespace(
    get_name(__name__),
    url_prefix='/{}'.format(get_name(__name__)),
)


@ns.route('/nested')
class NestedModel(Resource):
    @api.expect(UserModel)
    def post(self):
        return 'success'
