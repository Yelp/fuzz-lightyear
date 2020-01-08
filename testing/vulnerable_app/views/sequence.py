"""
These endpoints focus on testing the stateful-ness of the fuzzer.

The `alpha` series of endpoints enforce basic stateful-ness.
"""
from flask import abort
from flask_restplus import reqparse
from flask_restplus import Resource
from sqlalchemy.orm.exc import NoResultFound

from ..core import database
from ..core.auth import requires_user
from ..core.extensions import api
from ..models.widget import Widget
from ..parsers.basic import number_query_parser
from ..util import get_name
from .models.basic import string_model
from .models.database import widget_model


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


@ns.route('/bravo/one')
class BravoOne(Resource):
    @api.expect(number_query_parser)
    def post(self):
        return string_model.output()


@ns.route('/bravo/two')
class BravoTwo(Resource):
    @api.expect(number_query_parser)
    @api.response(200, 'Success', model=int)
    def get(self):
        return number_query_parser.parse_args()['id']


@ns.route('/side-effect/create')
class CreateWithSideEffect(Resource):
    @api.doc(security='apikey')
    @api.response(200, 'Success', model=widget_model)
    @requires_user
    def post(self, user):

        with database.connection() as session:
            entry = Widget()

            session.add(entry)
            session.commit()

            widget_id = entry.id

            user.created_resource = [entry.id]
            user.save()

        return {
            'id': widget_id,
        }


@ns.route('/side-effect/get/<int:id>')
class GetWithSideEffectUnsafe(Resource):
    @api.doc(security='apikey')
    @api.response(200, 'Success', model=widget_model)
    @api.response(404, 'Not Found')
    @requires_user
    def get(self, id, user):
        if not user.created_resource:
            abort(401)

        with database.connection() as session:
            try:
                entry = session.query(Widget).filter(
                    Widget.id == id,
                ).one()
            except NoResultFound:
                abort(404)

            widget_id = entry.id

        return {
            'id': widget_id,
        }


@ns.route('/side-effect-safe/get/<int:id>')
class GetWithSideEffectSafe(Resource):
    @api.doc(security='apikey')
    @api.response(200, 'Success', model=widget_model)
    @api.response(404, 'Not Found')
    @requires_user
    def get(self, id, user):
        if id not in user.created_resource:
            abort(403)

        with database.connection() as session:
            try:
                entry = session.query(Widget).filter(
                    Widget.id == id,
                ).one()
            except NoResultFound:
                abort(404)

            widget_id = entry.id

        return {
            'id': widget_id,
        }
