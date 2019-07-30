from flask_restplus import reqparse


number_query_parser = reqparse.RequestParser()
number_query_parser.add_argument(
    'id',
    type=int,
    required=True,
)


primitive_query_parser = reqparse.RequestParser()
primitive_query_parser.add_argument(
    'string',
    type=str,
    required=True,
)
primitive_query_parser.add_argument(
    'integer',
    type=int,
    required=True,
)
primitive_query_parser.add_argument(
    'number',
    type=float,
)
primitive_query_parser.add_argument(
    'boolean',
    type=bool,
)


location_parser = reqparse.RequestParser()
location_parser.add_argument(
    'query',
    location='args',
)
location_parser.add_argument(
    'form',
    location='form',
)
location_parser.add_argument(
    'header',
    location='headers',
)
