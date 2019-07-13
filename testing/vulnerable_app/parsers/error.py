from flask_restplus import reqparse


error_code_parser = reqparse.RequestParser()
error_code_parser.add_argument(
    'code',
    type=int,
    required=True,
)
