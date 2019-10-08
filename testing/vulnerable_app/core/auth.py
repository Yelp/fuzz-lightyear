from functools import wraps

from flask import abort
from flask import request
from sqlalchemy.orm.exc import NoResultFound

from . import database
from ..logic.user import User
from ..models.api_key import ApiKey
from .extensions import api


def requires_user(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            abort(401)

        with database.connection() as session:
            try:
                entry = session.query(ApiKey).filter(
                    ApiKey.api_key == api_key,
                ).one()
            except NoResultFound:
                abort(401)

        return func(*args, user=User(id=entry.id, **entry.user), **kwargs)

    return api.response(401, 'Unauthorized')(wrapped)
