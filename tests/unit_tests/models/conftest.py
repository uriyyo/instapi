from random import randint
from string import ascii_letters
from typing import (
    List,
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
    Resource,
)
from ..conftest import (
    random_int,
    random_string,
)


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
    Generate list of dummy feeds

    :param length: length of list
    :return: list of dummy feeds
    """
    return [
        Feed(
            pk=randint(1, 100),
            like_count=random_int(),
            comment_count=random_int(),
        ) for _ in range(length)
    ]


def create_resource(length: int = 10) -> List[Resource]:
    """
    Generate list of dummy resources

    :param length: length of list
    :return: list of dummy resources
    """
    return [
        Resource(
            url=f'http://{random_string(source=ascii_letters)}.com/{random_string(source=ascii_letters)}.jpg',
            width=random_int(),
            height=random_int(),
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


def create_comments(length: int = 10) -> List[Comment]:
    """
    Generate list of dummy comments

    :param length: length of list
    :return: list of dummy comments
    """
    return [
        Comment(
            text=random_string(),
            user=vars(create_users(length=1)[0]),
            pk=random_int(),
        ) for _ in range(length)
    ]


def create_feeds(length: int = 10) -> List[Feed]:
    """
    Generate list of dummy feeds

    :param length: length of list
    :return: list of dummy feeds
    """
    return [
        Feed(
            like_count=random_int(),
            comment_count=random_int(),
            pk=random_int(),
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
