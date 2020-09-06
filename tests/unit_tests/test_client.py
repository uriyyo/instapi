from instagram_private_api import Client
from pytest import (
    mark,
    raises,
)

from instapi.client import (
    bind,
    client,
)
from instapi.exceptions import ClientNotInitedException
from instapi.models import User
from .conftest import random_string


@mark.usefixtures('regular_client_mode')
def test_client_not_initialized():
    """Test for: bind function wasn't call"""
    with raises(ClientNotInitedException):
        User.self()


@mark.usefixtures('regular_client_mode')
def test_client_inited_after_bind(mocker):
    """Test for: bind function was called"""
    mocker.patch('instagram_private_api.client.Client.__init__', return_value=None)
    cookie_jar_mock = mocker.patch('instagram_private_api.client.Client.cookie_jar')
    get_from_cache_mock = mocker.patch('instapi.cache.get_from_cache', return_value=None)
    write_to_cache_mock = mocker.patch('instapi.cache.write_to_cache', return_value=None)

    username, password = random_string(), random_string()

    bind(username, password)

    # Check that proxy inited
    assert client.obj is not None
    Client.__init__.assert_called_once_with(username, password, cookie=None)

    get_from_cache_mock.assert_called_once_with((username, password))
    write_to_cache_mock.assert_called_once_with((username, password), cookie_jar_mock)


@mark.usefixtures('regular_client_mode')
def test_bind_with_no_arguments():
    with raises(ValueError):
        bind()
