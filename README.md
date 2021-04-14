[![Build Status](https://travis-ci.com/Yelp/fuzz-lightyear.svg?branch=master)](https://travis-ci.com/Yelp/fuzz-lightyear)

# fuzz-lightyear

<p align="center">
<img src="./docs/logo.png" width="200">
</p>

fuzz-lightyear is a [pytest-inspired](https://docs.pytest.org/en/latest/),
[DAST](https://en.wikipedia.org/wiki/Dynamic_Application_Security_Testing) framework,
capable of identifying vulnerabilities in a distributed, micro-service ecosystem through
**stateful** [Swagger](https://swagger.io/) fuzzing.

**What's Special About Stateful Fuzzing?**

Traditional fuzzing operates on the assumption that a command invocation failure is
indicative of a vulnerability. This approach does not carry over to web service fuzzing
since failures are **expected** to happen on bad input -- in fact, successful requests
with a purposely malicious payload is so much more dangerous, and should be caught
accordingly.

Stateful fuzzing allows us to do this. By keeping state between requests, we can assemble
a request sequence, and craft it to simulate a malicious attack vector and alert off
unexpected success. Using [hypothesis testing](https://hypothesis.readthedocs.io/en/latest/),
we're able to dynamically generate these test cases so we can continue to discover new
vectors. Finally, when we find an error, this testing framework outputs a list of cURL
commands for easy reproduction.

## Example

```
$ fuzz-lightyear https://petstore.swagger.io/v2/swagger.json -v --ignore-exceptions
```

## Installation

```
pip install fuzz-lightyear
```

## Usage

```
$ fuzz-lightyear -h

usage: fuzz-lightyear [-h] [-v] [--version] [-n [ITERATIONS]] [--schema SCHEMA]
                   [-f FIXTURE] [--seed SEED] [-t TEST] [--ignore-exceptions]
                   [--disable-unicode]
                   url

positional arguments:
  url                   URL of server to fuzz.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the verbosity of logging.
  --version             Displays version information.
  -n [ITERATIONS], --iterations [ITERATIONS]
                        Maximum request sequence length to fuzz.
  --schema SCHEMA       Path to local swagger schema. If provided, this
                        overrides theswagger file found at the URL.
  -f FIXTURE, --fixture FIXTURE
                        Path to custom specified fixtures.
  --seed SEED           Specify seed for generation of random output.
  -t TEST, --test TEST  Specifies a single test to run.
  --ignore-exceptions   Ignores all exceptions raised during fuzzing (aka.
                        only fails when vulnerabilities are found).
  --disable-unicode     Disable unicode characters in fuzzing, only use ASCII.

```

## Fixtures

Fixtures are a core component of `fuzz-lightyear`, and allow you to customize factories to
supplement fuzzing efforts for various endpoints. This is fundamentally important for
micro-service ecosystems, since services may not be CRUD applications by themselves.
This means the endpoints to create transient resources as part of the request sequence may
not be available in the Swagger specification.

To address this, we allow developers to supply custom commands necessary to populate
certain parts of the fuzzed request parameters.

### Example

Let's say that we have the following Swagger snippet:

```yaml
paths:
  /biz_user/{userID}/invoices:
    get:
      tags:
        - business
      operationId: "get_business_by_id"
      parameters:
        - name: "userID"
          in: "path"
          required: true
          type: integer
      responses:
        200:
          description: "success"
        403:
          description: "forbidden"
        404:
          description: "business not found"
```

We need a valid `userID` to access its invoices. Clearly, it would be a waste of time
for the fuzzer to put random values for the `userID`, because we don't care if an
attacker tries to access a business that doesn't exist. Moreover, this service
doesn't understand how to create a business (to obtain a valid `userID`), so the fuzzer
will not be effective at testing this endpoint.

To address this issue, we define a fixture to tell `fuzz-lightyear` how to handle such
cases.

```python
# fixtures.py
import fuzz_lightyear


@fuzz_lightyear.register_factory('userID')
def create_biz_user_id():
    return 1
```

Now, when `fuzz-lightyear` tries to fuzz `/biz_user/{userID}/invoices`, it will
identify that there's a user-defined factory for `userID`, and use its value in
fuzzing.

```bash
$ fuzz-lightyear -f fixtures.py http://localhost:5000/schema -v
================================== fuzzing session starts ==================================
Hypothesis Seed: 152367346948224061420843471695694220247

business E
====================================== Test Failures =======================================
_________________________ business.get_business_by_id [IDORPlugin] _________________________
Request Sequence:
[
  "curl -X GET http://localhost:5000/biz_user/1/invoices"
]
================================== 1 failed in 1.2 seconds =================================
```

We can amend this example by specifying a custom method to create a business in the
`create_business` function.

### Nested Fixtures

In keeping with the example above, let's say that you needed a business first, before you
can create a biz_user. We can accomplish this in the following method:

```python
# fixtures.py
import fuzz_lightyear


@fuzz_lightyear.register_factory('userID')
def create_biz_user_id(businessID):
    return businessID + 1


@fuzz_lightyear.register_factory('businessID')
def create_business():
    return 1
```

Then,

```bash
$ fuzz-lightyear -f fixtures.py http://localhost:5000/schema -v
================================== fuzzing session starts ==================================
Hypothesis Seed: 152367346948224061420843471695694220247

business E
====================================== Test Failures =======================================
_________________________ business.get_business_by_id [IDORPlugin] _________________________
Request Sequence:
[
  "curl -X GET http://localhost:5000/biz_user/2/invoices"
]
================================== 1 failed in 1.2 seconds =================================
```

We can also do type-casting of nested fixtures, through the use of **type annotations**.

```python
# fixtures.py
import fuzz_lightyear


@fuzz_lightyear.register_factory('userID')
def create_biz_user_id(businessID: str):
    return businessID + 'a'


@fuzz_lightyear.register_factory('businessID')
def create_business():
    return 1
```

Which will produce:

```bash
$ fuzz-lightyear -f fixtures.py http://localhost:5000/schema -v
================================== fuzzing session starts ==================================
Hypothesis Seed: 152367346948224061420843471695694220247

business E
====================================== Test Failures =======================================
_________________________ business.get_business_by_id [IDORPlugin] _________________________
Request Sequence:
[
  "curl -X GET http://localhost:5000/biz_user/1a/invoices"
]
================================== 1 failed in 1.2 seconds =================================
```

### Endpoint Specific Fixtures
Let's say that we have another endpoint , `get_user_by_id`, that requires a different kind of `userID`. We can't use the existing `userID` fixture, since it generates the wrong type of ID. We can solve this by writing an endpoint specific fixture.


```python
# fixtures.py
import fuzz_lightyear


@fuzz_lightyear.register_factory('userID')
def create_biz_user_id(businessID):
    return businessID + 1


@fuzz_lightyear.register_factory('userID', endpoint_ids=['get_user_by_id'])
def create_user_id():
    return 'foo'


@fuzz_lightyear.register_factory('businessID')
def create_business():
    return 1
```

Which will produce:

```bash
...
_________________________ user.get_user_by_id [IDORPlugin] _________________________
Request Sequence:
[
  "curl -X GET http://localhost:5000/user/foo"
]
================================== 1 failed in 1.2 seconds =================================
```

We can combine this with nested fixtures as well, but if we specify an endpoint in a fixture, every fixture that depends on that fixture will also need to specify the endpoint.

```python
# fixtures.py
import fuzz_lightyear


# We have to specify get_business_by_id here!
@fuzz_lightyear.register_factory('userID', endpoint_ids=['get_business_by_id'])
def create_biz_user_id(businessID):
    return businessID + 1


@fuzz_lightyear.register_factory('businessID', endpoint_ids=['get_business_by_id'])
def create_business():
    return 1
```

Which will produce:

```bash
...
_________________________ user.get_user_by_id [IDORPlugin] _________________________
Request Sequence:
[
  "curl -X GET http://localhost:5000/biz_user/2/invoices"
]
================================== 1 failed in 1.2 seconds =================================
```


### Authentication Fixtures

We can use fixtures to specify authentication/authorization methods to the Swagger
specification. This allows developers to customize the use of session cookies, or API
tokens, depending on individual use cases.

These fixtures are required for the `IDORPlugin`. We can include an `operation_id` argument in the fixture so that the operation id is automatically passed in. Other arguments will not be fuzzed.

```python
"""
These values are passed into the configured request method as keyword arguments.
Check out https://bravado.readthedocs.io/en/stable/advanced.html#adding-request-headers
for more info.
"""
import fuzz_lightyear


@fuzz_lightyear.victim_account
def victim_factory():
    return {
        '_request_options': {
            'headers': {
                'session': 'victim_session_id',
            },
        }
    }


@fuzz_lightyear.attacker_account
def attacker_factory():
    return {
        '_request_options': {
            'headers': {
                'session': 'attacker_session_id',
            }
        }
    }
```

### Setup Fixtures

We can use setup fixtures to specify code that we'd like to run _before_ any
tests are run. This allows developers to setup any custom configuration or
external applications the test application relies on.

```python
import fuzz_lightyear

@fuzz_lightyear.setup
def setup_function():
    print("This code will be executed before any tests are run")
```

### Including and excluding Swagger tags and operations

We can use fixtures to control whether fuzz-lightyear fuzzes certain parts of
the Swagger specification. This allows developers to only fuzz the parts
of the specification that can be fuzzed in the test environment.

```python
import fuzz_lightyear

@fuzz_lightyear.include.tags
def get_tags_to_fuzz():
    """fuzz_lightyear will only fuzz operations from
    these tags.
    """
    return ['user', 'transactions']


@fuzz_lightyear.exclude.operations
def get_operations_to_exclude():
    """fuzz_lightyear will not call these Swagger
    operations.
    """
    return [
        'get_user_id',
        'operation_doesnt_work_in_test_environment',
    ]


@fuzz_lightyear.exclude.non_vulnerable_operations
def get_non_vulnerable_operations():
    """fuzz_lightyear will not check these Swagger
    operations for vulnerabilities.

    This is different from `fuzz_lightyear.exclude.operations`
    in that these operations can still be executed by the
    fuzzer to generate request sequences, but the vulnerability
    plugins will not verify that these operations are secure.
    """
    # Accessing a user's public profile shouldn't require
    # authentication.
    return ['get_user_public_profile']
```

### Post-fuzz hooks

Sometimes factory fixtures and random fuzzing are not sufficient to
build a valid request. For example, the API could have an undeclared
required header, and it is unfeasible to add the header to the
Swagger spec. In this case, we can use post-fuzz hooks to transform
fuzzed data to a valid form.

```python
@fuzz_lightyear.hooks.post_fuzz(
    tags='user',
    operations='some_function',
    rerun=True,
)
def apply_nonce(
    operation: bravado.client.CallableOperation,
    fuzzed_data: Dict[str, Any],
) -> None:
    """This hook creates and adds a nonce to any request against
    operations with the 'user' tag, and additionally to the
    'some_function' operation.

    In addition, this nonce cannot be reused by a fuzz-lightyear
    request object, so we mark this hook is needing to be `rerun`.
    """
    nonce = make_nonce()
    fuzzed_data['nonce'] = nonce
```

Note: The order in which these hooks are run is not guaranteed.
