import json

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

from ..core.database import Base


class JSONType(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'

        return json.dumps(value)

    def process_result_value(self, value, dialect):
        # SQLite3 escapes single quotes with double single quotes
        return json.loads(value.replace("''", "'"))


class ApiKey(Base):
    user = Column(
        JSONType,
        nullable=False,
        doc=(
            'Let\'s be scrappy, and just store the user details in a mapping, '
            'rather than a separate table.'
        ),
    )
    api_key = Column(
        String,
        nullable=False,
        unique=True,
    )
