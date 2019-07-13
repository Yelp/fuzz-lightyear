from flask import Blueprint
from flask import jsonify
from flask import request

from ..views.basic import ns
from .extensions import api


def configure_routes(app):
    blueprint = Blueprint('api', __name__)
    api.init_app(blueprint)

    api.add_namespace(ns)

    app.register_blueprint(blueprint)

    app.route('/schema')(_get_schema)
    app.route('/shutdown', methods=['POST'])(_shutdown)


def _get_schema():
    return jsonify(api.__schema__)


def _shutdown():
    # Source: https://stackoverflow.com/a/17053522
    request.environ.get('werkzeug.server.shutdown')()
    return ''
