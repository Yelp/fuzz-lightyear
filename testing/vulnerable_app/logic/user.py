from ..core import database
from ..models.api_key import ApiKey


class User:
    def __init__(self, id, **kwargs):
        self.id = id
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        output = self.__dict__.copy()
        output.pop('id')

        return output

    def save(self):
        with database.connection() as session:
            entry = session.query(ApiKey).filter(
                ApiKey.id == self.id,
            ).one()

            entry.user = self.to_dict()

            session.commit()

    def __str__(self):
        output = 'User('
        output += ', '.join([
            f'{attr}={value}'
            for attr, value in self.__dict__.items()
        ])

        return output + ')'
