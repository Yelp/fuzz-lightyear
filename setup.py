from setuptools import find_packages
from setuptools import setup

from fuzzer_core import VERSION


setup(
    name='fuzzer_core',
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
    install_requires=[
        'bravado',
    ],
    entry_points={
        'console_scripts': [
            'fuzzer-core = fuzzer_core.main:main',
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
