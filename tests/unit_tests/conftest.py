from random import choice
from string import printable

from pytest import fixture

from instapi.client import ClientProxy


def pytest_configure():
    # Turn on testing mode for ClientProxy
    ClientProxy.is_testing = True


def random_string(length: int = 10, source: str = printable) -> str:
    """
    Generate random string from source string

    :param length: length of generated string
    :param source: source of characters to use
    :return: random string
    """
    return ''.join(choice(source) for _ in range(length))


@fixture()
def regular_client_mode():
    """
    Fixture that disable ClientProxy testing mode for single test
    """
    old_value = ClientProxy.is_testing
    ClientProxy.is_testing = False

    yield

    ClientProxy.is_testing = old_value
