from dataclasses import is_dataclass
from functools import partial
from random import choice, randint
from string import ascii_letters
from typing import Any, Callable, Dict, List, Type, TypeVar, Union

from pytest import fixture

from instapi import models
from instapi.client import ClientProxy

T = TypeVar("T")


def pytest_configure():
    # Turn on testing mode for ClientProxy
    ClientProxy.is_testing = True


def random_bytes(count: int = 10) -> bytes:
    """
    Generate random bytes

    :param count: how many bytes will be generated
    :return: random bytes
    """
    return b"".join(bytes(choice(ascii_letters), "ascii") for _ in range(count))


def random_string(length: int = 10, source: str = ascii_letters) -> str:
    """
    Generate random string from source string

    :param length: length of generated string
    :param source: source of characters to use
    :return: random string
    """
    return "".join(choice(source) for _ in range(length))


def random_int(start: int = 1, end: int = 100) -> int:
    """
    Generate a random int in range from start to end

    :param start: range start
    :param end: range end
    :return: a random int
    """
    return randint(start, end)


def random_url(extension: str = ".jpg"):
    """
    Generate random url

    :param extension: extension to add to url
    :return: random url
    """
    return f"http://{random_string()}.com/{random_string()}{extension}"


# Define default actions to do for different types
TYPE_TO_ACTION: Dict[Type, Callable] = {
    bool: partial(choice, [True, False]),
    int: random_int,
    str: random_string,
}


def _get_rand_type(field_type: Union[str, Type[T]]) -> T:
    """
    Create random field value based on type

    :param field_type: field type
    :return: random field value
    """
    if isinstance(field_type, str):
        field_type = getattr(models, field_type)

    if field_type in TYPE_TO_ACTION:
        return TYPE_TO_ACTION[field_type]()
    else:
        return rand(field_type)


def rand(cls: Type[T], **kwargs) -> T:
    """
    Generate an object from class with random fields values based on their types.
    Cls object must be wrapped with dataclass decorator to have ability
    fetch information about field types

    :param cls: object class to generate
    :param kwargs: kwargs to use at an instance
    :return: instance of cls with random fields values
    """
    if not is_dataclass(cls):
        raise TypeError("Can create random instances only of dataclass classes")

    fields_info = {f: cls.__dataclass_fields__[f] for f in cls.fields() if f not in kwargs}

    return cls(
        **{
            **{name: _get_rand_type(field.type) for name, field in fields_info.items()},
            **kwargs,
        }
    )


def rands(cls: Type[T], length: int = 10, **kwargs: Callable[[], Any]) -> List[T]:
    """
    Generate list of random objects

    :param cls: object type
    :param length: list size
    :param kwargs: fields overrides
    :return: list of random objects
    """
    return [rand(cls, **{k: v() for k, v in kwargs.items()}) for _ in range(length)]


@fixture()
def regular_client_mode():
    """
    Fixture that disable ClientProxy testing mode for single test
    """
    old_value = ClientProxy.is_testing
    ClientProxy.is_testing = False

    yield

    ClientProxy.is_testing = old_value
