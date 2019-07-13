from flask_restplus import reqparse


number_query_parser = reqparse.RequestParser()
number_query_parser.add_argument(
    'id',
    type=int,
    required=True,
)
