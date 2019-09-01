from itertools import chain
from random import randint
from string import ascii_letters

from typing import (
    List,
    Iterable,
    TypeVar,
)

from pytest import fixture

from instapi.models import (
    Comment,
    Feed,
    User,
)
from instapi.models.resource import (
    Image,
    Video,
)
from ..conftest import random_string

T = TypeVar('T')


def flat(source: List[Iterable[T]]) -> List[T]:
    """
    Unpack list of iterable into single list

    :param source: list of iterable
    :return: unpacked list
    """
    return [*chain.from_iterable(i for i in source)]


def random_int(start: int = 1, end: int = 100) -> int:
    """
    Generate a random int in range form start to end

    :param start: range start
    :param end: range end
    :return: a random int
    """
    return randint(start, end)


def create_users(length: int = 10) -> List[User]:
    """
    Generate list of dummy users

    :param length: length of list
    :return: list of dummy users
    """
    return [
        User(
            pk=randint(1, 100),
            username=random_string(),
            full_name=random_string(),
            is_private=False,
            is_verified=False,
        ) for _ in range(length)
    ]


def create_feeds(length: int = 10) -> List[Feed]:
    """
    Generate list of dummy feed

    :param length: length of list
    :return: list of dummy users
    """
    return [
        Feed(
            pk=randint(1, 100),
            like_count=random_int(),
            comment_count=random_int(),
        ) for _ in range(length)
    ]


def create_images(length: int = 10) -> List[Image]:
    """
    Generate list of dummy images

    :param length: length of list
    :return: list of dummy images
    """
    return [
        Image(
            url=f'http://{random_string(source=ascii_letters)}.com/{random_string(source=ascii_letters)}.jpg',
            width=random_int(),
            height=random_int(),
        ) for _ in range(length)
    ]


def create_videos(length: int = 10) -> List[Video]:
    """
    Generate list of dummy videos

    :param length: length of list
    :return: list of dummy videos
    """
    return [
        Video(
            url=f'http://{random_string(source=ascii_letters)}.com/{random_string(source=ascii_letters)}.mp4',
            width=random_int(),
            height=random_int(),
        ) for _ in range(length)
    ]


@fixture()
def user() -> User:
    """Fixture that return dummy user"""
    u, = create_users(length=1)
    return u


@fixture()
def feed() -> Feed:
    """Fixture that return dummy feed"""
    f, = create_feeds(length=1)
    return f


@fixture()
def comment(user) -> Comment:
    """Fixture that return comment with random content"""
    return Comment(
        pk=randint(1, 100),
        text='Random text',
        user=user,
    )
