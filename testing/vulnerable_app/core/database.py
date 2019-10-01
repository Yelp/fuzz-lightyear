import os
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import sessionmaker


@contextmanager
def connection():
    # TODO: This ought to be tied to the request lifecycle (rather than on-demand
    # creation of sessions). But since this is not a production app, we can ignore
    # this for now.
    session = create_session()

    try:
        yield session
    except InvalidRequestError:
        session.rollback()
    finally:
        session.close()


def create_session():
    return sessionmaker(
        bind=create_engine(),
        expire_on_commit=True,
    )()


@lru_cache(maxsize=1)
def create_engine():
    from sqlalchemy import create_engine
    return create_engine(f'sqlite:///{get_database_file()}')


def get_database_file():
    # NOTE: We're just using a known temporary file location, due to
    #       https://gehrcke.de/2015/05/in-memory-sqlite-database-and-flask-a-threading-trap/
    return os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            '../../db.sqlite3',
        ),
    )


class ModelBase:
    """
    An augmented base class for SqlAlchemy models.
    """

    @declared_attr
    def __tablename__(cls):
        """
        Return the lowercase class name as the name of the table.
        """
        return cls.__name__.lower()

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


Base = declarative_base(cls=ModelBase)
