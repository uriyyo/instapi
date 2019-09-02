from random import (
    choice,
    randint,
)
from string import printable

from pytest import fixture

from string import ascii_letters

from instapi.client import ClientProxy


def pytest_configure():
    # Turn on testing mode for ClientProxy
    ClientProxy.is_testing = True


def random_bytes(count: int = 10) -> bytes:
    """
    Generate random bytes

    :param count: how many bytes will be generated
    :return: random bytes
    """
    return b''.join(bytes(choice(ascii_letters), 'ascii') for _ in range(count))


def random_string(length: int = 10, source: str = printable) -> str:
    """
    Generate random string from source string

    :param length: length of generated string
    :param source: source of characters to use
    :return: random string
    """
    return ''.join(choice(source) for _ in range(length))


def random_int(start: int = 1, end: int = 100) -> int:
    """
    Generate a random int in range from start to end

    :param start: range start
    :param end: range end
    :return: a random int
    """
    return randint(start, end)


@fixture()
def regular_client_mode():
    """
    Fixture that disable ClientProxy testing mode for single test
    """
    old_value = ClientProxy.is_testing
    ClientProxy.is_testing = False

    yield

    ClientProxy.is_testing = old_value
