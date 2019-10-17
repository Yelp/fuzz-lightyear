from urllib.parse import quote_plus

from werkzeug.routing import BaseConverter


def get_name(name):
    """
    Blueprint names must be unique, and cannot contain dots.
    This converts filenames to blueprint names.

    e.g. vulnerable_app.views.basic => basic

    :type name: str
    """
    return name.split('.')[-1]


class ListConverter(BaseConverter):

    def __init__(self, url_map):
        super(ListConverter, self).__init__(url_map)
        self.delimiter = quote_plus(',')

    def to_python(self, value):
        return value.split(self.delimiter)

    def to_url(self, values):
        return self.delimiter.join(
            BaseConverter.to_url(value) for value in values
        )
