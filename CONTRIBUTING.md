# Contributing

## Layout

```
/fuzz_lightyear         # This is where the main code lives
  /output               # Output related functionality.
  /plugins              # Plugins for identifying security related issues.
  /supplements          # Handles dependency inversion and allows clients to
                        # specify various options for the engine.
  ...
  fuzzer.py             # Transforms Swagger requirements to hypothesis strategies.
  generator.py          # Generates request sequences to test.
  main.py               # Entrypoint for console use.
  runner.py             # Runs FuzzingRequest sequences and parses responses.

/test_data              # Sample files used for testing purposes.
/testing                # Common logic used in test cases.
  /vulnerable_app       # Sample server used for local testing and auto-generation
                        # of Swagger schema.
/tests                  # Mirrors fuzz_lightyear layout for all tests.
```

## Building Your Development Environment

```bash
$ pip install tox
$ make development
$ source venv/bin/activate
```

To check whether you're succesful, you can do:

```bash
$ python -m fuzz_lightyear --version
```

## Architecture

The overall flow for the fuzzer is rather straight-forward:
1. Generate request sequences of length=N.
2. Run each request sequence, to determine whether the request is successful, and whether
   it's expected to be successful.
3. Output results in a developer-friendly manner, so tests can be repeatable and
   proof-of-concepts are clear.

With this in mind, this system can be broken down into three main categories:
1. Generator
2. Test Runner
3. Formatter (for nice output)

### Generator

The generator is responsible for generating request sequences of length N, for a given
list of tests. It does so in a depth-first-search approach, so that the output will be
nicely formatted based on Swagger tags.

This is perhaps the most algorithmically challenging piece of this system. A longer
request sequence will result in an exponential growth in test cases to run, so we must
be selective in choosing valid request sequences, or aggressive at pruning them down.

Compatibility with a microservice ecosystem is an added layer of complexity. Unlike CRUD
apps where it's easier to reason about the creation and use of transient resources within
a single request sequence, a microservice may only contain selective parts of the whole
request sequence. This means it is more challenging to prune request sequences based on
known data, since we only have partial information from the Swagger specification.

We employ the following heuristics to perform request sequence pruning:

#### Successful Request Sequences Only

For a valid request sequence of length N, the sub-sequence of length N-1 must all return
valid responses. After all, there's no point continuing down a sequence of requests, if
there's a failure part way through.

### Test Runner

```
                                  -----------------
                                  | FuzzingResult |
                                  -----------------
                                /                \
                               /                  \
                              /                    \ ------------------
           ----------------- /                      | ResponseSequence |
          | FuzzingRequest <                         ------------------
          | FuzzingRequest <                        /              |
          |      ...       |                       /               |
           -----------------                      /                |
                                                 /                 |
                                            Sequence State         |
                                                              Analysis
                                                               Results
```

There are three main components to request sequence execution:
1. FuzzingRequest
2. ResponseSequence
3. FuzzingResult

#### FuzzingRequest

This is a wrapper around an API request to the server. It's an interface to the fuzzer
module and automatically fuzzes necessary parameters in a request. It's also responsible
for representing this request in a developer-friendly manner that allows for easy
reproduction of bugs.

Since this is a stateful Swagger fuzzer, a single run executes a number of `FuzzingRequest`s
in order (known as a sequence). The corresponding responses (and related state) is captured
in `ResponseSequence`.

#### ResponseSequence

The `ResponseSequence` object contains state relevant to API responses as a whole, and not
strictly related to requests. It contains some variables scoped to the entire response
sequence (e.g. transient resources created)

#### FuzzingResult

This is a thin wrapper around a namedtuple for (request, response). This pairing allows for
better manipulation of the data through the system.

### Formatter

All output formatting is abstracted into `fuzz_lightyear/output/interface.py`.
This allows it to keep state (e.g. aggregated warnings, timings) without having
it mangled with other core functionality code.

It primarily interacts with `FuzzingResult` instances, and is the main interface
between the rest of the application, and console output.

#### Logging

`fuzz_lightyear` has the ability to record logs per request sequence executed.
To allow for this functionality, we have captured all logs to a string stream
so that we have better control on when / where these logs are displayed. This
string stream is then manually cleared per request sequence iteration.

Access to this logging interface is simple:

```python
from fuzz_lightyear.output.logging import log
log.info('Test message!')
```

These logs will only appear on the request sequences that fail.

## Testing

We use `pytest` as a test runner. To run the entire suite of tests, you can do:

```bash
make test
```

### Integration Tests

To facilitate easier development (and faster testing), we use `Flask` and `Flask-RestPlus`
to create a purposely vulnerable application in `testing/vulnerable_app`. In doing so,
we're able to spin this server up, extract the Swagger schema for it, run our testing
framework against a real server, and finally shut it down -- all encapsulated in the test
run.

To write integration tests:

1. Create a new endpoint in `testing/vulnerable_app/views`, with models and request
   parsers as needed.

```python
from flask_restplus import Resource

from ..core.extensions import api
from ..util import get_name


ns = api.namespace(
    get_name(__name__),
    url_prefix='/{}'.format(get_name(__name__)),
)


@ns.route('/')
class ClassName(Resource):
    def get(self):
        return ''
```

2. Use the `mock_client` fixture in `tests/integration`.

```python
def test_example(mock_client):
    # Test logic goes here!
    pass
```

3. Reference the newly created endpoint!

```python
from fuzz_lightyear.request import FuzzingRequest
def test_example(mock_client):
    # Naming format:
    #   tag = filename of views/ endpoint you created in step #1.
    #   operation_id = concatenation of {http_method}_{camel_case_class_name}
    # The below example reference step #1, assuming that you created this new
    # endpoint in `testing/vulnerable_app/views/filename.py`.
    FuzzingRequest(
        operation_id='get_class_name',
        tag='filename',
    ).send()
```

### Manual Testing

You can spin up the vulnerable application by doing:

```bash
$ make vulnerable_app
```

Then, in a different tab, you can run:

```bash
$ fuzz-lightyear http://localhost:5000/schema -f test_data
```

Only one instance will be running at a single time, so if you manually spin up the server,
then run your integration tests, you will be able to see the requests coming in.

You can also see the generated Swagger specification by doing:

```bash
$ python -m testing.mock_server | jq
```
