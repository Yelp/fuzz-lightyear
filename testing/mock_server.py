import json
import logging
import os
from contextlib import contextmanager
from contextlib import redirect_stdout
from time import sleep

import requests
from multiprocess import Process

from testing.vulnerable_app.__main__ import main as start_server


PORT = int(os.environ.get('PORT', 5000))
URL = 'http://localhost:{}'.format(PORT)


def get_mock_schema():
    with vulnerable_server():
        return requests.get('{}/schema'.format(URL)).json()


@contextmanager
def vulnerable_server():
    def spin_up_server():
        # Make the server silent.
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        with open(os.devnull, 'w') as f, redirect_stdout(f):
            start_server()

    starting_up = False
    is_it_up = is_server_up()
    if not is_it_up:
        starting_up = True
        Process(
            target=spin_up_server,
        ).start()

        while not is_it_up:
            sleep(1)
            is_it_up = is_server_up()

    try:
        yield
    finally:
        if starting_up:
            requests.post('{}/shutdown'.format(URL))


def is_server_up():
    try:
        return requests.get(URL).status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def get_path(path='.'):
    """
    :type path: str
    :param path: relative path from this file
    """
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            path,
        ),
    )


if __name__ == '__main__':
    print(json.dumps(get_mock_schema()))
