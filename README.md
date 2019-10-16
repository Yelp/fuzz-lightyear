[![Build Status](https://travis-ci.com/Yelp/fuzz-lightyear.svg?branch=master)](https://travis-ci.com/Yelp/fuzz-lightyear)

# fuzz-lightyear

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
usage: fuzz-lightyear [-h] [-v] [-n [ITERATIONS]] [--schema SCHEMA] [-f FIXTURE]
                   [--seed SEED]
                   url

positional arguments:
  url                   URL of server to fuzz.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase the verbosity of logging.
  -n [ITERATIONS], --iterations [ITERATIONS]
                        Maximum request sequence length to fuzz.
  --schema SCHEMA       Path to local swagger schema. If provided, this
                        overrides theswagger file found at the URL.
  -f FIXTURE, --fixture FIXTURE
                        Path to custom specified fixtures.
  --seed SEED           Specify seed for generation of random output.
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

### Authentication Fixtures

We can use fixtures to specify authentication/authorization methods to the Swagger
specification. This allows developers to customize the use of session cookies, or API
tokens, depending on individual use cases.

These fixtures are required for the `IDORPlugin`.

```python
"""
These values are passed into the configured request method as keyword arguments.
"""
import fuzz_lightyear


@fuzz_lightyear.victim_account
def victim_factory():
    return {
        'headers': {
            'session': 'victim_session_id',
        },
    }


@fuzz_lightyear.attacker_account
def attacker_factory():
    return {
        'headers': {
            'session': 'attacker_session_id',
        }
    }
```
