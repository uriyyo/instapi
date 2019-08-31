from random import (
    choice,
    randint,
)
from string import printable

from pytest import fixture

from instapi.models import (
    Comment,
    User,
)


def random_string(length: int = 10) -> str:
    """
    Generate random string from printable characters

    :param length: length of generated string
    :return: random string
    """
    return ''.join(choice(printable) for _ in range(length))


@fixture()
def user():
    """Fixture that return dummy user"""
    return User(
        pk=randint(1, 100),
        username=random_string(),
        full_name=random_string(),
        is_private=False,
        is_verified=False,
    )


@fixture()
def comment(user):
    """Fixture that return comment with random content"""
    return Comment(
        pk=randint(1, 100),
        text='Random text',
        user=user,
    )
