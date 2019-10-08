"""
Mainly used for setup.
"""
import random
import string

from flask_restplus import Resource

from ..core import database
from ..core.auth import requires_user
from ..core.extensions import api
from ..models.api_key import ApiKey
from ..util import get_name
from .models.database import user_model


ns = api.namespace(
    get_name(__name__),
    url_prefix='/{}'.format(get_name(__name__)),
)


@ns.route('/create')
class CreateUser(Resource):
    @api.response(200, 'Success', model=str)
    def post(self):
        api_key = random_string(20)
        with database.connection() as session:
            entry = ApiKey(api_key=api_key)

            session.add(entry)
            session.commit()

        return api_key


@ns.route('/')
class GetUser(Resource):
    @api.doc(security='apikey')
    @api.response(200, 'Success', model=user_model)
    @requires_user
    def get(self, user):
        return {
            'user_id': user.id,
            **user.to_dict(),
        }


def random_string(k=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(k))
