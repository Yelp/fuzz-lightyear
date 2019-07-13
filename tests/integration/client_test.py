import pytest
from bravado.exception import HTTPError


def test_success(mock_client):
    assert mock_client.constant.get_no_inputs_required().result().value == 'ok'


def test_error(mock_client):
    with pytest.raises(HTTPError) as e:
        mock_client.constant.get_will_throw_error(code=400).result()

    assert e.value.status_code == 400
