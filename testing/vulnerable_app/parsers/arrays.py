from flask_restplus import reqparse


boolean_array_parser = reqparse.RequestParser()
boolean_array_parser.add_argument(
    'array',
    action='append',
    type=bool,
)


string_array_parser = reqparse.RequestParser()
string_array_parser.add_argument(
    'csv',
    action='split',
    type=str,
    location='form',
)


required_array_parser = reqparse.RequestParser()
required_array_parser.add_argument(
    'array',
    action='append',
    type=bool,
    required=True,
)
