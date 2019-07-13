def test_success(mock_client):
    assert mock_client.constant.get_no_inputs_required().result().value == 'ok'
