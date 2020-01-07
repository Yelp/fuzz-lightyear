"""
These endpoints focus on testing the stateful-ness of the fuzzer.

The `alpha` series of endpoints enforce basic stateful-ness.
"""
from flask import abort
from flask_restplus import Resource
from sqlalchemy.orm.exc import NoResultFound

from ..core import database
from ..core.auth import requires_user
from ..core.extensions import api
from ..models.thing import Thing
from ..util import get_name
from .models.database import thing_model


ns = api.namespace(
    get_name(__name__),
    url_prefix='/{}'.format(get_name(__name__)),
)


# This tests that https://github.com/Yelp/fuzz-lightyear/issues/11 has been fixed.
@ns.route('/no-vuln/create')
class CreateNoVuln(Resource):
    @api.doc(security='apikey')
    @api.response(200, 'Success', model=thing_model)
    @requires_user
    def post(self, user):

        with database.connection() as session:
            entry = Thing()

            session.add(entry)
            session.commit()

            user.created_resource = [entry.id]
            user.save()

        return {
            'id': entry.id,
        }


@ns.route('/no-vuln/get/<int:id>')
class GetNoVuln(Resource):
    @api.doc(security='apikey')
    @api.response(200, 'Success', model=thing_model)
    @api.response(404, 'Not Found')
    @api.response(403, 'Not Authorized')
    @requires_user
    def get(self, id, user):
        if id not in user.created_resource:
            abort(403)

        with database.connection() as session:
            try:
                entry = session.query(Thing).filter(
                    Thing.id == id,
                ).one()
            except NoResultFound:
                abort(404)

            widget_id = entry.id

        return {
            'id': widget_id,
        }
