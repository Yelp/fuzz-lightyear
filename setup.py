from setuptools import find_packages
from setuptools import setup

from fuzz_lightyear import VERSION


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
        'hypothesis',
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
        'Development Status :: 3 - Alpha',
    ],
)
