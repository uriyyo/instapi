from instapi.client_api.base import BaseClient
from ..conftest import random_string


def test_redirect_to_base(mocker):
    mocker.patch('instagram_private_api.client.Client.__init__', return_value=None)
    mock = mocker.patch('instagram_private_api.client.Client._call_api', return_value=None)

    client = BaseClient(random_string(), random_string())
    client._call_api(random_string())

    mock.assert_called_once()
