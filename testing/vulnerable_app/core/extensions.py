from flask_restplus import Api


api = Api(
    version='1.0',
    title='Vulnerable App',
    description='Collection of vulnerable endpoints to test fuzzing with.',
)
