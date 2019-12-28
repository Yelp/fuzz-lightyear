import os

from setuptools import find_packages
from setuptools import setup


def local_file(path):
    return os.path.relpath(
        os.path.join(
            os.path.dirname(__file__),
            path,
        ),
    )


# We can't import fuzz_lightyear.version, since it pulls in all other
# fuzz_lightyear modules. Therefore, we need to execute the file
# directly.
VERSION = None      # needed for flake8
with open(local_file('fuzz_lightyear/version.py')) as f:
    exec(f.read())


setup(
    name='fuzz_lightyear',
    packages=find_packages(exclude=(['test*', 'tmp*'])),
    version=VERSION,
    description='Vulnerability Discovery through Stateful Swagger Fuzzing',
    license='Copyright Yelp, Inc. 2019',
    author=', '.join([
        'Aaron Loo <aaronloo@yelp.com>',
        'Joey Lee <joeylee@yelp.com>',
        'Victor Zhou <vzhou@yelp.com>',
    ]),
    keywords=[
        'fuzzer',
        'security',
        'swagger',
    ],
    # Remember to update requirements-minimal.txt when making changes
    # to this list.
    install_requires=[
        'bravado',
        'cached-property',
        'hypothesis>=4.56.1',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'fuzz-lightyear = fuzz_lightyear.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Topic :: Security',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing :: Acceptance',
        'Topic :: Utilities',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
    ],
)
